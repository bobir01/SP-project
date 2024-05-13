import io
import logging
import signal
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, PhotoImage, Toplevel, Entry, Button, TOP

from ps_utils import ProcessManager, SystemInformation
from utils import uni2dt, format_float
from tg_bot import TelegramSocketClient


class ProcessMonitoringGUI(object):
    def __init__(self, _root, process_data_len=6):
        self.process_data = None
        self.logger = logging.getLogger(__name__)
        self.root = _root

        self.pm = ProcessManager()
        self.style = ttk.Style(self.root)
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
        self.refresh_button = tk.Button(self.top_frame, text="Refresh 🔄")
        self.refresh_button.pack(side=tk.RIGHT)
        self.refresh_button.bind("<Button-1>", self.refresh_processes)
        # dump button
        self.dump_button = tk.Button(self.top_frame, text="Dump ⬇️")
        self.dump_button.pack(side=tk.RIGHT)
        self.dump_button.bind("<Button-1>", self.dump_fnc)

        # telegram button
        self.telegram_button = tk.Button(self.top_frame, text="Telegram 📱")
        self.telegram_button.pack(side=tk.RIGHT)
        self.telegram_button.bind("<Button-1>", self.popupwin)

        # process list
        self.raw_columns = ('Pid', 'Name', 'Status', 'CPU %', 'Memory %', 'Create Time', 'Nice', 'Username', 'Threads',)
        self.columns = self.pm.process_attributes[0:len(self.raw_columns)]
        self.process_list = ttk.Treeview(self.list_frame, columns=self.raw_columns, show='headings', style='Treeview')
        self.process_list.bind('<<TreeviewSelect>>', self.update_selected)

        self.signals = {'SIGINT': signal.SIGINT, 'SIGALRM': signal.SIGALRM, 'SIGHUP': signal.SIGHUP,
                        'SIGTERM': signal.SIGTERM}
        self.signals_emoji = {'SIGINT': '🛑', 'SIGALRM': '⏰', 'SIGHUP': '🔄', 'SIGTERM': '🛑'}

        self.base_dir = Path(__file__).parent.resolve()

        for col in self.raw_columns:
            self.process_list.heading(col, text=col)
        self.process_list.pack(fill=tk.BOTH, expand=True)
        # buttons declaration
        for sig in self.signals.keys():
            button = tk.Button(self.button_frame, text=sig + ' ' + self.signals_emoji.get(sig, '🚦'))
            button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
            button.bind("<Button-1>", self.send_signal)
        # initial population of process list
        self.refresh_processes(None)

        # Define a function to close the popup window

    def close_win(self, top):
        top.destroy()

    def popupwin(self, event):
        #Popup that takes telegra id and send message
        top = Toplevel(self.root)
        top.geometry("750x250")
        top.title("Insert Telegram ID")

        # Create an Entry Widget in the Toplevel window
        entry = Entry(top, width=25)
        entry.pack()
        entry.insert(0, "Enter your TG ID here...")
        entry.focus_set()
        entry.bind('<FocusIn>', self.focus_in_tg_id)
        entry.bind('<FocusOut>', self.focus_out_tg_id)
        self.tg_id = entry



        send_msg = Button(top, text="Send message ✉️")
        send_msg.bind("<Button-1>", self.send_telegram_message)
        send_msg.pack(pady=5, side=TOP)
        # Create a Button Widget in the Toplevel Window
        button = Button(top, text="Ok", command=lambda: self.close_win(top))
        button.pack(pady=5, side=TOP)

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

    def focus_out_tg_id(self, event):
        if event.widget.get() == '':
            event.widget.insert(0, 'Enter your TG ID here...')
            event.widget.config(fg='grey')

    def focus_in_tg_id(self, event):
        if event.widget.get() == 'Enter your TG ID here...':
            event.widget.delete(0, "end")
            event.widget.config(fg='white')


    def refresh_processes(self, event=None):
        self.process_list.delete(*self.process_list.get_children())
        self.process_data = self.pm.get_processes()
        # ['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'create_time',
        #                                    'exe',  'nice', 'username'
        for proc in self.process_data:
            self.process_list.insert("", "end", values=(
                proc['pid'],
                proc['name'],
                proc['status'],
                format_float(proc['cpu_percent']),
                format_float(proc['memory_percent']),
                uni2dt(proc['create_time']).strftime('%Y-%m-%d %H:%M:%S'),
                proc.get('nice', ''),
                proc.get('username', ''),
                format_float(proc.get('num_threads', 1)),

            ), iid=proc['pid'])

    def refresh_pm(self):
        self.process_data = self.pm.get_processes()

    def send_signal(self, event):
        """general function to send a signal to a process."""
        signal_name = event.widget.cget('text')
        signal_name = signal_name.split(' ')[0]  # remove emoji
        if self.selected_pid:
            try:
                self.logger.info(f"Sending signal {signal_name} to PID {self.selected_pid}")
                signal = self.signals[signal_name]
                self.pm.send_signal(int(self.selected_pid), signal)
                signal_emoji = self.signals_emoji.get(signal_name, '🚦')
                messagebox.showinfo(
                    f"Signal Sent {signal_emoji}",
                    f"Signal {signal_name} {signal_emoji} sent to PID {self.selected_pid}")
            except Exception as e:
                self.logger.error(f"Error sending signal {signal_name} to PID {self.selected_pid}: {e}")
                messagebox.showerror("Error",
                                     f"Error sending signal {signal_name} to PID {self.selected_pid}, Not enough permissions.🥲")

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
            selected_item = selected_item[0]  # Assuming the PID is in the first column
            self.selected_pid = selected_item
            return selected_item
        self.logger.debug(f"Selected item: {selected_item}")

    def run(self):
        self.root.mainloop()

    def set_aux(self):
        icon = PhotoImage(file=self.base_dir / 'assets' / 'icon.png')
        self.root.iconphoto(False, icon)
        self.root.title("Process Monitor")
        self.root.geometry("1200x800")
        self.root.wm_minsize(800, 600)

    def dump_fnc(self, event):
        self.logger.info("Dumping process data")
        with open(self.base_dir / 'assets' / 'processes.csv', 'w') as f:
            f.write(','.join(self.pm.process_attributes) + '\n')
            for proc in self.process_data:
                f.write(','.join([str(proc.get(attr, '')) for attr in self.pm.process_attributes]) + '\n')
        messagebox.showinfo("Dumped", "Process data dumped to processes.csv")
        logging.info("Process data dumped to %sprocesses.csv", self.base_dir / 'assets/')

    def send_telegram_message(self, event):

        tg_id = self.tg_id.get()
        self.logger.info(f"Telegram ID: {tg_id}")
        if tg_id == 'Enter your TG ID here...':
            messagebox.showerror("Error", "Please enter your Telegram ID")
            return
        if not tg_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid Telegram ID")
            return
        if tg_id.strip() == '':
            tg_id = 881939669
            self.logger.info("Sending message to Telegram uses socket client")
        tg = TelegramSocketClient('7155087790:AAEQIRoSeZ6CsXDb-ltJXCJHe44_ZBAKDZA', tg_id)  # 881939669
        sys_info: io.StringIO = SystemInformation().collect_into_strIO()
        res = tg.send_telegram_message(sys_info.getvalue())
        if res.get('ok'):
            messagebox.showinfo("Sent ✅", "✅ Message sent to Telegram to Boss 🫡 ;)")
        else:
            messagebox.showerror("Error", "Error sending message to Telegram %s" % res.get('description'))
        logging.info("Message sent to Telegram")


if __name__ == '__main__':
    root = tk.Tk()
    logging.basicConfig(level=logging.INFO)
    pmg = ProcessMonitoringGUI(root)
    pmg.set_aux()
    pmg.run()
