import psutil
from typing import List, Dict, Any
import io

import pprint
import re


class ProcessManager:
    def __init__(self):
        self.processes: List[Dict] = []
        self.process_attributes = ['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'create_time',
                                   'nice', 'username', 'num_threads',
                                   'exe',  'cmdline', ]

    def get_processes(self) -> List[Dict[str, Any]]:
        """Get list of all processes running on the system."""
        self.processes = []
        for proc in psutil.process_iter(attrs=self.process_attributes):
            try:
                self.processes.append(proc.as_dict(attrs=self.process_attributes))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return sorted(self.processes, key=lambda x: x['pid'], reverse=True)

    def get_process_by_pid(self, pid: int) -> List[Dict[str, Any]]:
        """Get process by PID.
        :param pid: Process ID.
        :return: Process object.
        """
        patrn = re.compile(f'{pid}', flags=re.IGNORECASE)
        return [proc for proc in self.processes if patrn.match(str(proc.get('pid')))]

    def get_process_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Get list of processes by name.
        :param name: Process name.
        :return: List of process objects."""
        re_pattern = re.compile(name, flags=re.IGNORECASE)
        return [proc for proc in self.processes if re_pattern.match(proc['name'])]

    def renice_process(self, pid: int, nice: int) -> None:
        """Change the priority of a process.
        :param pid: Process ID.
        :param nice: New priority value."""
        proc = self.get_process_by_pid(pid)
        proc.nice(nice)

    def kill_process(self, pid: int) -> None:
        """Kill a process by PID.
        :param pid: Process ID."""
        proc = psutil.Process(pid)
        proc.kill()

    def send_signal(self, pid: int, signal: int) -> None:
        """Send a signal to a process.
        :param pid: Process ID.
        :param signal: Signal to send."""
        proc = psutil.Process(pid)
        proc.send_signal(signal)


class SystemInformation:
    def __init__(self):
        pass

    # Function to convert bytes to a human-readable format
    def bytes_to_human_readable(self, bytes):
        for unit in ['', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024

    def get_cpu_information(self):
        cpu_percent = str(psutil.cpu_percent())
        cpu_count = str(psutil.cpu_count())
        cpu_freq = str(psutil.cpu_freq())
        return cpu_percent, cpu_count, cpu_freq

    def get_memory_information(self):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        mem_total = self.bytes_to_human_readable(mem.total)
        mem_available = self.bytes_to_human_readable(mem.available)
        mem_used = self.bytes_to_human_readable(mem.used)
        mem_free = self.bytes_to_human_readable(mem.free)
        swap_total = self.bytes_to_human_readable(swap.total)
        swap_used = self.bytes_to_human_readable(swap.used)
        swap_free = self.bytes_to_human_readable(swap.free)

        return mem_total, mem_available, mem_used, mem_free, swap_total, swap_used, swap_free

    def get_num_processes(self):
        num_processes = str(len(psutil.pids()))
        return num_processes

    def print_system_information(self):
        cpu_percent, cpu_count, cpu_freq = self.get_cpu_information()
        mem_total, mem_available, mem_used, mem_free, swap_total, swap_used, swap_free = self.get_memory_information()
        num_processes = self.get_num_processes()
        print("\nCPU Percent:", cpu_percent)
        print("CPU Count:", cpu_count)
        print("CPU Frequency:", cpu_freq)
        print("\nMemory:")
        print("Total:", mem_total)
        print("Available:", mem_available)
        print("Used:", mem_used)
        print("Free:", mem_free)
        print("\nSwap Memory:")
        print("Total:", swap_total)
        print("Used:", swap_used)
        print("Free:", swap_free)
        print("\nNumber of Running Processes:", num_processes)

    def collect_into_strIO(self):
        """Collect all system info into a string buffer"""
        cpu_percent, cpu_count, cpu_freq = self.get_cpu_information()
        mem_total, mem_available, mem_used, mem_free, swap_total, swap_used, swap_free = self.get_memory_information()
        num_processes = self.get_num_processes()
        sio = io.StringIO()

        # Use emojis to make the output more interactive and visually appealing
        sio.write("\n🔧 CPU Percent: " + str(cpu_percent) + "%\n")
        sio.write("🧮 CPU Count: " + str(cpu_count) + "\n")
        sio.write("⚙️ CPU Frequency: " + str(cpu_freq) + " MHz\n")
        sio.write("\n💾 Memory:\n")
        sio.write("📊 Total: " + str(mem_total) + " MB\n")
        sio.write("🟢 Available: " + str(mem_available) + " MB\n")
        sio.write("🔴 Used: " + str(mem_used) + " MB\n")
        sio.write("🟢 Free: " + str(mem_free) + " MB\n")
        sio.write("\n🔄 Swap Memory:\n")
        sio.write("📊 Total: " + str(swap_total) + " MB\n")
        sio.write("🔴 Used: " + str(swap_used) + " MB\n")
        sio.write("🟢 Free: " + str(swap_free) + " MB\n")
        sio.write("\n🚦 Number of Running Processes: " + str(num_processes) + "\n")

        return sio



if __name__ == '__main__':
    pm = ProcessManager()
    pcs = pm.get_processes()
    # pcs[-1].kill()
    pprint.pprint(pcs[0])
    # kill the last process-2
    print("done")
