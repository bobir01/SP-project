import psutil
from typing import List, Dict, Any

import pprint
import re


class ProcessManager:
    def __init__(self):
        self.processes: List[Dict] = []
        self.process_attributes = ['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'create_time',
                                   'exe', 'nice', 'username', 'num_threads', 'cmdline', ]

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


if __name__ == '__main__':
    pm = ProcessManager()
    pcs = pm.get_processes()
    # pcs[-1].kill()
    pprint.pprint(pcs[0])
    # kill the last process-2
    print("done")
