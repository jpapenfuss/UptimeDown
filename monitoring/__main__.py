#import commands
from gather import cpu, memory, filesystems
#import logging
# see log_setup.py
from log_setup import log_setup


def main():
    # See log_setup.py
    logger = log_setup()
    refresh_delay = 1
    import json
    mycpu = cpu.Cpu()
    mymemory = memory.Memory()
    myfs = filesystems.Filesystems()

    print(json.dumps({"cpustats": mycpu.cpustat_values, "cpuinfo": mycpu.cpuinfo_values, "memory": mymemory.stats, "filesystems": myfs.filesystems}, indent=4))

if __name__ == "__main__":
    main()
