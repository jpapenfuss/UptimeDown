import time
import logging

logger = logging.getLogger("monitoring")


class Memory:
    stats = {}

    def GetMeminfo(self):
        # Path definitions
        meminfo_path = "/proc/meminfo"
        meminfo_values = {}

        if util.caniread(meminfo_path) is False:
            logger.error(f"Fatal: Can't open {meminfo_path} for reading.")
            exit(1)
        # Read all of cpuinfo into a list for data collection
        with open(meminfo_path, "r") as reader:
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

    def GetSlabinfo(self):
        slabs = {}
        if (util.caniread("/proc/slabinfo")) is False:
            logger.warning(
                "Can't read /proc/slabinfo - I may not be root. Will not collect slab stats"
            )
            return False
        with open("/proc/slabinfo", "r") as reader:
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

    def __init__(self):
        logger.info("Initializing Memory Gathering")
        # On instantiation, get meminfo. We'll also call GetMemInfo on updates.
        self.stats["memory"] = self.GetMeminfo()
        self.stats["slabs"] = self.GetSlabinfo()


if __name__ == "__main__":
    import util  # pylint: disable=import-error
    import pprint

    pp = pprint.PrettyPrinter(indent=4)
    mymemory = Memory()
    pp.pprint(mymemory.stats)
else:
    from . import util
