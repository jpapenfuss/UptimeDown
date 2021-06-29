import time
import logging

logger = logging.getLogger("monitoring")


class Cpu:
    INTEGER_STATS = [
        "apicid",
        "btime",
        "cache_alignment",
        "clflush size",
        "core id",
        "cpu cores",
        "cpu family",
        "cpuid level",
        "ctxt",
        "guest",
        "guest_nice",
        "idle",
        "initial apicid",
        "iowait",
        "irq",
        "model",
        "nice",
        "physical id",
        "processes",
        "processor",
        "procs_blocked",
        "procs_running",
        "siblings",
        "steal",
        "stepping",
        "system",
        "user",
    ]
    FLOAT_STATS = ["bogomips", "cpu MHz"]
    LIST_STATS = ["flags", "bugs", "softirq"]

    def GetCpuinfo(self):
        cpuinfo_values = {}
        # Path definitions
        cpuinfo_path = "/proc/cpuinfo"

        # Read all of cpuinfo into a list for data collection
        with open(cpuinfo_path, "r") as reader:
            # read first line
            cpuinfo_line = str(reader.readline()).strip()
            # loop until a blank line. This will get us cpu0's config, which is
            # probably plenty.
            while cpuinfo_line != "":
                # Split on colon:
                # model name      : AMD EPYC 7571
                split = cpuinfo_line.split(":")
                # trim leading and trailing whitespace for key and value then reassign since we reference it multiple times. "model name"
                split[0] = split[0].strip()
                split[1] = split[1].strip()
                if split[0] in self.INTEGER_STATS:
                    cpuinfo_values[split[0]] = int(split[1])
                elif split[0] in self.FLOAT_STATS:
                    cpuinfo_values[split[0]] = float(split[1])
                elif split[0] in self.LIST_STATS:
                    cpuinfo_values[split[0]] = split[1].split()
                # add key:value to dict cpuinfo_values
                else:
                    cpuinfo_values[split[0]] = split[1]

                # Get the next line.
                cpuinfo_line = str(reader.readline()).strip()

        cpuinfo_values["_time"] = time.time()
        return cpuinfo_values

    def GetCpuProcStats(self):
        cpustats_values = {}
        cpustats_values['stats'] = {}
        stat_path = "/proc/stat"
        with open(stat_path, "r") as reader:
            stat_line = str(reader.readline()).strip()
            while stat_line != "":
                if stat_line.startswith("cpu"):
                    split = stat_line.split()
                    # cpu_name is cpu if it's the total metrics for the cpu
                    # it's cpuN for each core/hyperthread
                    cpu_name = split[0]
                    split.pop(0)
                    # cpu  545171 4295 203016 140708647 12297 0 6426 232949 0 0
                    # cpu0 272044 2628 100726 70358155 6200 0 3286 102134 0 0
                    # cpu1 273126 1667 102289 70350492 6097 0 3139 130815 0 0
                    cpustats_values['stats'][cpu_name] = {
                        "user": int(split[0]),
                        "nice": int(split[1]),
                        "system": int(split[2]),
                        "idle": int(split[3]),
                        "iowait": int(split[4]),
                        "irq": int(split[5]),
                        "softirq": int(split[6]),
                        "steal": int(split[7]),
                        "guest": int(split[8]),
                        "guest_nice": int(split[9]),
                    }

                elif stat_line.startswith("intr"):
                    # We're not going to deal with the mess of shit that is the interrupts here.
                    pass

                else:
                    # We split the line, as we always do
                    split = stat_line.split()
                    key = split[0]
                    # The 0 index is now assigned to our key, so get it out of the way.
                    split.pop(0)
                    if key in self.INTEGER_STATS:
                        cpustats_values[key] = int(split[0])
                    elif key in self.FLOAT_STATS:
                        cpustats_values[key] = float(split[0])
                    else:
                        cpustats_values[key] = split
                stat_line = str(reader.readline()).strip()
        cpustats_values['_time'] = time.time()
        return cpustats_values

    def UpdateValues(self):
        self.cpuinfo_values = self.GetCpuinfo()
        self.cpustat_values = self.GetCpuProcStats()

    def __init__(self):
        # We want to get initial data on first instantiation.
        self.UpdateValues()


if __name__ == "__main__":
    import pprint

    pp = pprint.PrettyPrinter(indent=4)
    mycpu = Cpu()
    pp.pprint(mycpu.cpustat_values)
    pp.pprint(mycpu.cpuinfo_values)
