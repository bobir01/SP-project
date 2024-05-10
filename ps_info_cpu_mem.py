import psutil

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


sys_info = SystemInformation()
sys_info.print_system_information()