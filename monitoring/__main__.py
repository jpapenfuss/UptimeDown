import time

timestart = time.time()
# import commands
from gather import cpu, memory, filesystems, disk

# import logging
# see log_setup.py
from log_setup import log_setup


def main():
    # See log_setup.py
    logger = log_setup()
    import json

    logger.debug("Gathering CPU stats.")
    mycpu = cpu.Cpu()
    logger.debug("Gathering memory stats.")
    mymemory = memory.Memory()
    logger.debug("Gathering filesystem stats.")
    myfs = filesystems.Filesystems()
    logger.debug("Gathering disk stats.")
    mydisks = disk.Disk()

    jsonout = json.dumps(
        {
            "cpustats": mycpu.cpustat_values,
            "cpuinfo": mycpu.cpuinfo_values,
            "memory": mymemory.stats,
            "filesystems": myfs.filesystems,
            "disks": mydisks.blockdevices,
        },
        indent=4,
    )

    print(jsonout)


if __name__ == "__main__":
    main()
