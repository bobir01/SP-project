import logging
import signal
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ps_utils import ProcessManager
from datetime import datetime
from typing import List, Dict, Any
from utils import uni2dt, format_float
import re


class ProcessMonitoringGUI(object):
    def __init__(self, _root, process_data_len=6):
        self.process_data = None
        self.logger = logging.getLogger(__name__)
        self.root = _root
        self.root.title("Process Monitor")
        self.root.geometry("1200x800")
        self.root.wm_minsize(800, 600)
        self.style = ttk.Style(self.root)
        self.pm = ProcessManager()
        self.style.configure('TButton', font=('Helvetica', 12), background='black', foreground='white')
        self.style.configure('TEntry', font=('Helvetica', 12), background='black', foreground='white')
        self.style.configure('TLabel', font=('Helvetica', 12), background='black', foreground='white')
        self.selected_pid = None
        # frames
        self.top_frame = tk.Frame(self.root, background='black')
        self.top_frame.pack(fill=tk.X)
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(fill=tk.BOTH, expand=True)
        self.button_frame = tk.Frame(self.root, background='black')
        self.button_frame.pack(fill=tk.X)
        # search entry
        self.search_entry = tk.Entry(self.top_frame, font=('Helvetica', 12), fg='grey', width=50)
        self.search_entry.insert(0, 'Search process...')
        self.search_entry.bind('<FocusIn>', self.on_entry_click)
        self.search_entry.bind('<FocusOut>', self.on_focusout)
        self.search_entry.bind('<KeyRelease>', self.search_processes)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, padx=20, pady=20)
        # refresh button
        self.refresh_button = tk.Button(self.top_frame, text="Refresh")
        self.refresh_button.pack(side=tk.RIGHT)
        self.refresh_button.bind("<Button-1>", self.refresh_processes)
        # process list
        self.raw_columns = ('Pid', 'Name', 'Status', 'CPU %', 'Memory %', 'Create Time')
        self.columns = self.pm.process_attributes[0:process_data_len]
        self.process_list = ttk.Treeview(self.list_frame, columns=self.raw_columns, show='headings', style='Treeview')
        self.process_list.bind('<<TreeviewSelect>>', self.update_selected)

        self.signals = {'SIGINT': signal.SIGINT, 'SIGALRM': signal.SIGALRM, 'SIGHUP': signal.SIGHUP,
                        'SIGTERM': signal.SIGTERM}

        for col in self.raw_columns:
            self.process_list.heading(col, text=col)
        self.process_list.pack(fill=tk.BOTH, expand=True)
        # signal buttons
        # self.signals = ['SIGINT', 'SIGALRM', 'SIGHUP', 'SIGTERM']
        for sig in self.signals.keys():
            button = tk.Button(self.button_frame, text=sig)
            button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
            button.bind("<Button-1>", self.send_signal)
        # initial population of process list
        self.refresh_processes(None)

    def on_entry_click(self, event):
        if self.search_entry.get() == 'Search process...':
            self.search_entry.delete(0, "end")
            # self.search_entry.insert(0, '')
            self.search_entry.config(fg='white')

    def on_focusout(self, event):
        if self.search_entry.get() == '':
            self.search_entry.insert(0, 'Search process...')
            self.search_entry.config(fg='grey')
            self.refresh_processes()

    def refresh_processes(self, event=None):
        self.process_list.delete(*self.process_list.get_children())
        self.process_data = self.pm.get_processes()
        # ['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'create_time',
        #                                    'exe',  'nice', 'username'
        for proc in self.process_data:
            self.process_list.insert("", "end", values=(
                proc['pid'], proc['name'], proc['status'],
                format_float(proc['cpu_percent']),

                format_float(proc['memory_percent']),
                uni2dt(proc['create_time']).strftime('%Y-%m-%d %H:%M:%S'),
                # proc['exe'],  proc['nice'], proc['username']
            ), iid=proc['pid'])

    def refresh_pm(self):
        self.process_data = self.pm.get_processes()

    def send_signal(self, event):
        """general function to send a signal to a process."""
        signal_name = event.widget.cget('text')
        if self.selected_pid:
            try:
                self.logger.info(f"Sending signal {signal_name} to PID {self.selected_pid}")
                self.pm.send_signal(int(self.selected_pid), self.signals[signal_name])
                messagebox.showinfo("Signal Sent", f"Signal {signal_name} sent to PID {self.selected_pid}")
            except Exception as e:
                self.logger.error(f"Error sending signal {signal_name} to PID {self.selected_pid}: {e}")


    def search_processes(self, event):
        """Based on the search entry, let's filter the process list."""
        name_or_pid = self.search_entry.get()
        if name_or_pid == 'Search process...':
            return
        else:
            for item in self.process_list.get_children():
                self.process_list.delete(item)

        if name_or_pid.isdigit():
            # search by PID
            pid = int(name_or_pid)
            self.refresh_pm()
            for process in self.pm.get_process_by_pid(pid):
                if process['pid'] == pid:
                    self.process_list.insert('', 'end', values=(
                        process['pid'], process['name'], process['status'],
                        format_float(process['cpu_percent']),
                        format_float(process['memory_percent']),
                        uni2dt(process['create_time']).strftime('%Y-%m-%d %H:%M:%S'),
                    ))


        else:
            # search by name
            self.process_data = self.pm.get_process_by_name(name_or_pid)
            self.refresh_pm()
            for proc in self.pm.get_process_by_name(name_or_pid):
                self.process_list.insert("", "end", values=(
                    proc['pid'], proc['name'], proc['status'],
                    format_float(proc['cpu_percent']),
                    format_float(proc['memory_percent']),
                    uni2dt(proc['create_time']).strftime('%Y-%m-%d %H:%M:%S'),
                ))

    # Function to update the currently selected process ID
    def update_selected(self, event):
        self.logger.info("Updating selected process")
        selected_item = self.process_list.selection()
        if selected_item:

            self.logger.info(f"Selected item: {selected_item}")
            selected_item = selected_item[0] # Assuming the PID is in the first column
            self.selected_pid = selected_item
            return selected_item
        self.logger.debug(f"Selected item: {selected_item}")

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    root = tk.Tk()
    logging.basicConfig(level=logging.INFO)
    pmg = ProcessMonitoringGUI(root)
    pmg.run()
