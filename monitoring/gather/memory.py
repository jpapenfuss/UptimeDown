import time
import logging

logger = logging.getLogger("monitoring")
# Constants
MEMINFO_PATH = "/proc/meminfo"
VMSTAT_PATH = "/proc/vmstat"
SLABINFO_PATH = "/proc/slabinfo"


class Memory:
    stats = {}

    def GetMeminfo(self):
        # Path definitions
        meminfo_values = {}

        if util.caniread(MEMINFO_PATH) is False:
            logger.error(f"Fatal: Can't open {MEMINFO_PATH} for reading.")
            exit(1)
        # Read all of cpuinfo into a list for data collection
        with open(MEMINFO_PATH, "r") as reader:
            # read in first line
            meminfo_line = str(reader.readline()).strip()
            # Iterate until EOF
            while meminfo_line != "":
                # Substitutes the regex compiled as stripper.sub for single-spaces
                meminfo_line = meminfo_line.replace(":", " ")
                # Split on single space
                line = meminfo_line.split()
                # coerce second value into int, it should only ever be a number
                line[1] = int(line[1])

                # If we have 3 values, it's Key:Value:Multiplier (kB/mB/gB)
                # I have no idea if the multiplier can be anything but kB.
                if len(line) == 3:
                    line[1] = util.tobytes(line[1], line[2])
                # Set key:value into meminfo_values dict
                meminfo_values[line[0]] = line[1]

                # read mext line for next iteration
                meminfo_line = str(reader.readline()).strip()
        meminfo_values["_time"] = time.time()
        return meminfo_values

    def GetVmstats(self):
        vmstats = {}
        if (util.caniread(VMSTAT_PATH)) is False:
            logger.warning("Can't read VMSTAT_PATH, returning false.")
            return False
        with open(VMSTAT_PATH, "r") as reader:
            vmstatline = reader.readline()
            while vmstatline != "":
                stat = vmstatline.split()
                vmstats[stat[0]] = int(stat[1])
                vmstatline = reader.readline()
        return vmstats

    def GetSlabinfo(self):
        slabs = {}
        if (util.caniread(SLABINFO_PATH)) is False:
            logger.warning(
                "Can't read /proc/slabinfo - I may not be root. Will not collect slab stats"
            )
            return False
        with open(SLABINFO_PATH, "r") as reader:
            slabline = reader.readline()
            while slabline != "":
                if slabline.startswith("slabinfo") or slabline.startswith("# name"):
                    # Burner line, continue
                    slabline = reader.readline()
                    continue
                # Each line is three sets of stats, broken into sections with colons:
                # ext4_inode_cache   30338  44330   1096   29    8 : tunables    0    0    0 : slabdata   2834   2834      0
                slabline = slabline.replace(": tunables", "").replace(": slabdata", "")
                # ext4_inode_cache   30338  44330   1096   29    8     0    0    0    2834   2834      0
                # Split on whitespace.
                slab = slabline.strip().split()
                # Remove first entry in list, which will be the object name, and assign value to slabname
                slabname = slab.pop(0)
                # Coerce values to ints, create dicts
                # 'ext4_inode_cache': {'active_objs': 21292, 'active_slabs': 1370,
                # 'batchcount': 0, 'limit': 0, 'num_objs': 39730, 'num_slabs': 1370,
                # 'objperslab': 29, 'objsize': 1096, 'pagesperslab': 8,
                # 'sharedavail': 0, 'sharedfactor': 0},
                slabs[slabname] = dict(
                    zip(
                        [
                            "active_objs",
                            "num_objs",
                            "objsize",
                            "objperslab",
                            "pagesperslab",
                            "limit",
                            "batchcount",
                            "sharedfactor",
                            "active_slabs",
                            "num_slabs",
                            "sharedavail",
                        ],
                        list(map(int, slab)),
                    )
                )
                # Get next line
                slabline = reader.readline()
        slabs["_time"] = time.time()
        return slabs

    def UpdateValues(self, gatherslabs=True, gathermeminfo=True, gathervmstat=True):
        # On instantiation, get meminfo. We'll also call GetMemInfo on updates.
        if gathermeminfo is True:
            logger.debug("Memory: Calling GetMeminfo()")
            # Call me paranoid, but we purge any existing metrics and declare the object.
            self.stats["memory"] = {}
            self.stats["memory"] = self.GetMeminfo()

        if gatherslabs is True:
            logger.debug("Memory: Calling GetSlabinfo()")
            # Call me paranoid, but we purge any existing metrics blah blah.
            self.stats["slabs"] = {}
            self.stats["slabs"] = self.GetSlabinfo()

        if gathervmstat is True:
            logger.debug("Memory: Calling GeVmstats()")
            self.stats["vmstats"] = {}
            self.stats["vmstats"] = self.GetVmstats()

    def __init__(self):
        logger.info("Memory: Initial Memory Gathering")
        self.UpdateValues()


if __name__ == "__main__":
    import util  # pylint: disable=import-error
    import pprint

    pp = pprint.PrettyPrinter(indent=4)
    mymemory = Memory()
    pp.pprint(mymemory.stats)
else:
    from . import util
