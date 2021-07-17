#import commands
from gather import cpu, memory, filesystems
#import logging
# see log_setup.py
from log_setup import log_setup


def main():
    # See log_setup.py
    logger = log_setup()
    refresh_delay = 1

    mycpu = cpu.Cpu()
    mymemory = memory.Memory()
    myfs = filesystems.Filesystems()
    print(mycpu.cpustat_values)
    print(mycpu.cpuinfo_values)
    print(mymemory.stats)
    print(myfs.filesystems)

if __name__ == "__main__":
    main()
