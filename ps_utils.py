import psutil
import os
import sys
import time
from pathlib import Path
from pydantic import BaseModel
from typing import List, Dict, Any


# here we implement the class for the process with pydantic

class Process(BaseModel):
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    create_time: float
    cwd: str
    exe: str
    cmdline: str
    niceness: int
    username: str



#class that will be generating the process list and managing the process #fixme add the process manager funct
class ProcessManager:
    pass
