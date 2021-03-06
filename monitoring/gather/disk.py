import logging
import os
import time

logger = logging.getLogger("monitoring")


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

# This seems universal?
SYS_BLOCK_PATH = "/sys/block/"
# /sys/class/block was not present on my QNAP NAS running kernel 4.14
SYS_CLASS_BLOCK_PATH = "/sys/class/block/"
# Directory with device numbers, symlinked to proper subsystems.
SYS_DEV_BLOCK_PATH = "/sys/dev/block/"
# /proc/diskstats has a good chunk of what we need and I wonder if there's anything in /sys/block that wouldn't be in there, or named differently.
PROC_DISKSTATS_PATH = "/proc/diskstats"


class Disk:

    blockdevices = {}

    def get_devices(self):
        diskstats = {}
        skip_zero_io = True
        if util.caniread(PROC_DISKSTATS_PATH) is False:
            logger.error(f"Fatal: Can't open {PROC_DISKSTATS_PATH} for reading.")
            return None

        with open(PROC_DISKSTATS_PATH, "r") as reader:
            logger.debug(f"Disk: Reading {PROC_DISKSTATS_PATH}")
            # 8       0 sda 6812071 23231120 460799263 43073497 9561353 55255999 547604986 81837974 0 93365790 124928542
            diskstats_line = str(reader.readline()).strip().split()
            while diskstats_line != []:
                # if there's no read IO or write IO, skip it. Quote zeros here as we haven't converted to int yet.
                if (
                    diskstats_line[3] == "0"
                    and diskstats_line[7] == "0"
                    and skip_zero_io is True
                ):
                    logger.debug(f"Disk: Skipping {diskstats_line[2]} with no IO")
                    diskstats_line = str(reader.readline()).strip().split()
                    continue
                # or skip if device name starts with prefixes in our ignore list
                elif diskstats_line[2].startswith(tuple(IGNORE_PREFIXES)):
                    logger.debug(f"Disk: Skipping excluded device {diskstats_line[2]}")
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
        dev = {}

        # Get the details of one device by device number.
        path = os.path.realpath(os.path.join(SYS_DEV_BLOCK_PATH, devnum))
        uevent_path = os.path.join(path, "uevent")
        if util.caniread(uevent_path) is False:
            logger.error(f"Disk: Fatal: Can't open {uevent_path} for reading.")
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
            # This is dirty, just go up one directory and use that path to determine disk that partition occupies.
            dev["PARTITION_OF"] = os.path.basename(
                os.path.realpath(os.path.join(dev["realpath"], ".."))
            )
        return dev

    def get_disk_model(self, devnum):
        path = os.path.join(SYS_DEV_BLOCK_PATH, devnum, "device/model")
        path = os.path.realpath(path)
        if util.caniread(path) is False:
            logger.debug(f"Disk: Can't read {path} to determine device model.")
            return False
        with open(path) as reader:
            model = str(reader.readline()).strip()
        return model

    def get_disk_serial(self, devnum):
        path = os.path.join(SYS_DEV_BLOCK_PATH, devnum, "device/serial")
        path = os.path.realpath(path)
        if util.caniread(path) is False:
            logger.debug(f"Disk: Can't read {path} to determine device serial.")
            return False
        with open(path) as reader:
            serial = str(reader.readline()).strip()
        return serial

    def get_disk_firmware(self, devnum):
        path = os.path.join(SYS_DEV_BLOCK_PATH, devnum, "device/firmware_rev")
        path = os.path.realpath(path)
        if util.caniread(path) is False:
            logger.debug(f"Disk: Can't read {path} for device firmware.")
            return False
        with open(path) as reader:
            firmware = str(reader.readline()).strip()
        return firmware

    def get_disk_queue(self, devnum):
        # Does this even matter? None of these are especially compelling details.
        queue = {}
        path = os.path.join(SYS_DEV_BLOCK_PATH, devnum, "queue")
        path = os.path.realpath(path)
        with os.scandir(path) as files:
            for f in files:
                if f.is_file():
                    filename = f.name
                else:
                    continue
                queuefile = os.path.join(path, filename)
                with open(queuefile) as reader:
                    # Some files are special, and may not be readable in certain
                    # situations. For example, an md0 device that's defined but
                    #  doesn't actually exist has wbt_lat_usec but it's not
                    # readable.
                    try:
                        queue[filename] = str(reader.readline()).strip()
                    except:
                        queue[filename] = False
                        logger.debug(f"Can't open {queuefile} for reading.")
                    # Python has string methods for .isdigit(), .isnumeric(),
                    # .isdecimal(), but none of these match on negative
                    # numbers OR floats. So we just jackhammer everything and
                    # see what sticks. Dumb as hell.
                    try:
                        queue[filename] = int(queue[filename])
                    except:
                        pass
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
            # the path to the real sysfs directory tree, resolving through symlinks.
            devs[dev]["path"] = ret["realpath"]
            # type = disk or partition
            devs[dev]["type"] = ret["DEVTYPE"]
            if devs[dev]["type"] == "partition":
                devs[dev]["partition_number"] = ret["PARTN"]
                devs[dev]["partition_of"] = ret["PARTITION_OF"]
            if devs[dev]["type"] == "disk":
                devs[dev]["queuestats"] = self.get_disk_queue(devnum)
                devs[dev]["model"] = self.get_disk_model(devnum)
                devs[dev]["serial"] = self.get_disk_serial(devnum)
                devs[dev]["firmware"] = self.get_disk_firmware(devnum)
        return devs

    def __init__(self):
        self.blockdevices = self.get_disks()


if __name__ == "__main__":
    import pprint
    import util  # pylint: disable=import-error

    pp = pprint.PrettyPrinter(indent=4)

    mydisk = Disk()
    pp.pprint(mydisk.blockdevices)
else:
    from . import util
