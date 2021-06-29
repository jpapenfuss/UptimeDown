import re
import time
import logging
import util

logger = logging.getLogger("monitoring")


class Memory:
    def GetMeminfo(self):
        # Path definitions
        meminfo_path = "/proc/meminfo"
        meminfo_values = {}

        if util.caniread(meminfo_path) is False:
            logger.error(f"Fatal: Can't open {meminfo_path} for reading.")
            exit(1)
        # Read all of cpuinfo into a list for data collection
        with open(meminfo_path, "r") as reader:
            stripper = re.compile(r"(:)?\s+")
            # read in first line
            meminfo_line = str(reader.readline()).strip()
            # Iterate until EOF
            while meminfo_line != "":
                # Substitutes the regex compiled as stripper.sub for single-spaces
                line = stripper.sub(" ", meminfo_line, count=0)
                # Split on single space
                line = line.split()
                # coerce second value into int, it should only ever be a number
                line[1] = int(line[1])

                # If we have 3 values, it's Key:Value:Multiplier (kB/mB/gB)
                # I have no idea if the multiplier can be anything but kB.
                if len(line) == 3:
                    if line[2] == "kB":
                        # kB to Bytes
                        line[1] = line[1] * 1024
                    elif line[2] == "mB":
                        # mB to Bytees
                        line[1] = line[1] * 1024 * 1024
                    elif line[2] == "gB":
                        # gB to Bytes
                        line[1] = line[1] * 1024 * 1024 * 1024
                    elif line[2] == "tB":
                        # WTF are you doing?
                        line[1] = line[1] * 1024 * 1024 * 1024 * 1024

                # Set key:value into meminfo_values dict
                meminfo_values[line[0]] = line[1]

                # read mext line for next iteration
                meminfo_line = str(reader.readline()).strip()
        meminfo_values["_time"] = time.time()
        return meminfo_values

    def FindInMeminfo(self, searchstring):
        return self.meminfo_values[searchstring]

    def GetSlabinfo(self):
        slabs = {}
        if (util.caniread('/proc/slabinfo')) is False:
            logger.warning("Can't read /proc/slabinfo - I may not be root. Will not collect slab stats")
            return False
        with open('/proc/slabinfo', "r") as reader:
            slabline = reader.readline()
            while slabline != "":
                if slabline.startswith('slabinfo') or slabline.startswith('# name'):
                    # Burner line, continue
                    slabline = reader.readline()
                    continue

                line = slabline.split(':')
                slab = str(line[0]).strip().split()
                slabname = slab.pop(0)
                slabs[slabname] = dict(zip(["active_objs", "num_objs", "objsize", "objperslab"], list(map(int, slab))))

                slabtunables = str(line[1]).strip().split()
                slabtunables.pop(0)
                slabs[slabname]['tunables'] = dict(zip(["limit", "batchcount", "sharedfactor"], list(map(int, slabtunables))))

                slabdata = str(line[2]).strip().split()
                slabdata.pop(0)
                slabs[slabname]['slabdata'] = dict(zip(["active_slabs", "num_slabs", "sharedavail"], list(map(int, slabdata))))

                slabline = reader.readline()
        slabs['_time'] = time.time()
        return slabs

    def __init__(self):
        logger.info("Initializing Memory Gathering")
        # On instantiation, get meminfo. We'll also call GetMemInfo on updates.
        self.meminfo_values = self.GetMeminfo()
        self.slabinfo_values = self.GetSlabinfo()

if __name__ == "__main__":
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    mymemory = Memory()
    pp.pprint(mymemory.meminfo_values)
    pp.pprint(mymemory.slabinfo_values)
