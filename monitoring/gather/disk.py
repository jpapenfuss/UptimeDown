"""
https://www.kernel.org/doc/Documentation/ABI/testing/procfs-diskstats
https://www.kernel.org/doc/Documentation/block/statca.txt

259       0 nvme0n1 107146 2852 19971336 23647 181355 11090 15833592 22852 0 66784 92500 13669 0 1758032920 52066
259       1 nvme1n1 109518 3015 19983994 23593 172156 11064 15588608 22670 0 73196 98604 13669 0 1757785272 52757
  9     127 md127 222424 0 48560354 0 333649 0 37421048 0 0 0 0 13669 0 3515818192 0
"""

# https://www.kernel.org/doc/Documentation/admin-guide/iostats.rst

# NFS stats: http://git.linux-nfs.org/?p=steved/nfs-utils.git;a=blob;f=tools/mountstats/mountstats.py;hb=HEAD
import logging
import os
import pprint
import time

logger = logging.getLogger("monitoring")
"""
loop = loopback
ram = ram
nbd = network block device https://www.kernel.org/doc/html/latest/admin-guide/blockdev/nbd.html, we may want to monitor these
fbdisk = ?
fbsnap = ?
zram = Compressed memory as block store https://www.kernel.org/doc/html/latest/admin-guide/blockdev/zram.html
"""

IGNORE_PREFIXES = [
    "loop",
    "ram",
]
DISKSTAT_KEYS = (
    "major",
    "minor",
    #        "name",
    "read_ios",
    "read_merge",
    "read_sectors",
    "read_ticks",
    "write_ios",
    "write_merges",
    "write_sectors",
    "write_ticks",
    "in_flight",
    "total_io_ticks",
    "total_time_in_queue",
    "discard_ios",
    "discard_merges",
    "discard_sectors",
    "discard_ticks",
    "flush_ios",
    "flush_ticks",
)
# files in /sys/block/DEV/* we care about.
# inflight: gives read and write ops inflight. Maybe not really useful for monitoring, but diskstats only gives one value.
# queue/: https://www.kernel.org/doc/Documentation/block/queue-sysfs.txt
BLOCK_FILES = [
    "inflight",
    "size",
    "queue/discard_granularity",
    "queue/hw_sector_size",
    "queue/io_poll",
    "queue/io_poll_delay",
    "queue/io_timeout",
    "queue/iostats",
    "queue/logical_block_size",
    "queue/max_hw_sectors_kb",
    "queue/max_sectors_kb",
    "queue/minimum_io_size",
    "queue/nomerges",
    "queue/optimal_io_size",
    "queue/physical_block_size",
    "queue/read_ahead_kb",
    "queue/rotational",
    "queue/rq_affinity",
    "queue/scheduler",
    "queue/write_cache",
]
# For the purposes of these stats, we are focusing solely on block devices.
class Disk:
    # This seems universal?
    sys_block_path = "/sys/block/"
    # /sys/class/block was not present on my QNAP NAS running kernel 4.14
    sys_class_block_path = "/sys/class/block/"
    # Directory with device numbers, symlinked to proper subsystems.
    sys_dev_block_path = "/sys/dev/block/"
    # /proc/diskstats has a good chunk of what we need and I wonder if there's anything in /sys/block that wouldn't be in there, or named differently.
    proc_diskstats_path = "/proc/diskstats"

    blockdevices = {}

    def get_devices(self):
        diskstats = {}
        if util.caniread(self.proc_diskstats_path) is False:
            logger.error(f"Fatal: Can't open {self.proc_diskstats_path} for reading.")
            return None

        with open(self.proc_diskstats_path, "r") as reader:
            # 8       0 sda 6812071 23231120 460799263 43073497 9561353 55255999 547604986 81837974 0 93365790 124928542
            diskstats_line = str(reader.readline()).strip().split()
            while diskstats_line != []:
                if diskstats_line[2].startswith(tuple(IGNORE_PREFIXES)):
                    # If we're ignoring the device type, read the next line and return to start of loop.
                    diskstats_line = str(reader.readline()).strip().split()
                    continue
                # If we get the name out of the way, everything else is an int. And we want to index off the name anyway.
                diskname = diskstats_line.pop(2)
                diskstats[diskname] = {
                    "iostats": dict(zip(DISKSTAT_KEYS, list(map(int, diskstats_line))))
                }
                diskstats[diskname]["_time"] = time.time()

                diskstats_line = str(reader.readline()).strip().split()
        return diskstats

    def get_sys_dev_block(self, devnum):
        # Get the details of one device by device number.
        path = os.path.realpath(os.path.join(self.sys_dev_block_path, devnum))
        uevent_path = path + "/uevent"
        # We'll return dev when it's populated. Create dict here.
        dev = {}
        if util.caniread(uevent_path) is False:
            logger.error(f"Fatal: Can't open {uevent_path} for reading.")
            return False
        # Store the resolved path of the block device - This is often a symlink. Always a symlink?
        # /sys/dev/block/259:0 -> /sys/devices/pci0000:00/0000:00:04.0/nvme/nvme0/nvme0n1
        dev["realpath"] = path
        # uevent has the broad details of almost any sysfs directory. This contains:
        #  MAJOR, MINOR, DEVNAME (nvme0n1p1), DEVTYPE (disk, partition), PARTN (partition number)
        with open(uevent_path) as reader:
            # entries are INI-style, NAME=VALUE so split on equal sign.
            line = str(reader.readline()).strip().split("=")
            # Empty split will equal [""]
            while line != [""]:
                # These are numeric items, so coerce to int
                if line[0] in ["MAJOR", "MINOR", "PARTN"]:
                    line[1] = int(line[1])
                dev[line[0]] = line[1]
                line = str(reader.readline()).strip().split("=")
        if dev["DEVTYPE"] == "partition":
            dev["PARTITION_OF"] = os.path.basename(os.path.realpath(os.path.join(dev["realpath"], "..")))
        logger.debug(f"get_sys_dev_block returning {dev} for {devnum}")
        return dev

    def get_disk_queue(self, devnum):
        queue = {}
        path = os.path.realpath(os.path.join(self.sys_dev_block_path, devnum, "queue"))
        for file in os.listdir(path):
            queuefile = os.path.join(path, file)
            with open(queuefile) as reader:
                # Some files are special, and may not be readable in certain situations.
                # For example, an md0 device that's defined but doesn't have members has
                # wbt_lat_usec but it's not readable.
                try:
                    queue[file] = str(reader.readline()).strip()
                except:
                    queue[file] = False
                    logger.warning(f"Can't open {queuefile} for reading.")
                # Python has string methods for .isdigit(), .isnumeric(), .isdecimal(), but none of these
                # match on negative numbers OR floats. So we just jackhammer everything and see what sticks.
                try:
                    queue[file] = int(queue[file])
                except:
                    #todo: this is definitely a debug message, at most.
                    logger.warning(f"Can't coerce {file}: {queue[file]} to int")
        return queue

    def get_disks(self):
        # First let's do the easy thing and get the stats that exist in diskstats:
        devs = self.get_devices()
        for dev in devs:
            devnum = (
                str(devs[dev]["iostats"]["major"])
                + ":"
                + str(devs[dev]["iostats"]["minor"])
            )
            ret = self.get_sys_dev_block(devnum)
            devs[dev]["path"] = ret["realpath"]
            devs[dev]["type"] = ret["DEVTYPE"]
            if devs[dev]["type"] == "partition":
                devs[dev]["partition_number"] = ret["PARTN"]
                devs[dev]["partition_of"] = ret["PARTITION_OF"]
            if devs[dev]["type"] == "disk":
                devs[dev]["queuestats"] = self.get_disk_queue(devnum)
        return devs

    def __init__(self):
        self.blockdevices = self.get_disks()


if __name__ == "__main__":
    import util  # pylint: disable=import-error

    mydisk = Disk()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(mydisk.blockdevices)
else:
    from . import util
