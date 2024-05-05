import psutil
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Union
from decimal import Decimal
import re


# class that will be generating the process list and managing the process #fixme add the process manager funct
class ProcessManager:
    def __init__(self):
        self.processes: List[psutil.Process] = []
        self.process_attributes = ['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'create_time',
                                   'exe', 'cmdline', 'nice', 'username', 'num_threads']

    def get_processes(self) -> List[psutil.Process]:
        """Get list of all processes running on the system."""
        self.processes = []
        for proc in psutil.process_iter(attrs=self.process_attributes):
            try:
                self.processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return self.processes

    def get_process_by_pid(self, pid: int) -> psutil.Process:
        """Get process by PID.
        :param pid: Process ID.
        :return: Process object.

        :raises: NoSuchProcess"""
        return psutil.Process(pid)

    def get_process_by_name(self, name: str) -> List[psutil.Process]:
        """Get list of processes by name.
        :param name: Process name.
        :return: List of process objects."""
        re_pattern = re.compile(name)
        return [proc for proc in self.processes if re_pattern.match(proc.name())]

    def renice_process(self, pid: int, nice: int) -> None:
        """Change the priority of a process.
        :param pid: Process ID.
        :param nice: New priority value."""
        proc = self.get_process_by_pid(pid)
        proc.nice(nice)


if __name__ == '__main__':
    pm = ProcessManager()
    pcs = pm.get_processes()
    # pcs[-1].kill()
    print("done")
