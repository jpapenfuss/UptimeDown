import time
import logging

logger = logging.getLogger("monitoring")
# Constants
CPUINFO_PATH = "/proc/cpuinfo"
SOFTIRQ_PATH = "/proc/softirqs"
STAT_PATH = "/proc/stat"


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
        if util.caniread(CPUINFO_PATH) is False:
            logger.warning(f"Can't read {CPUINFO_PATH}, bailing out.")
            # While we can't read CPU info for some reason, we don't sys.exit
            # as other modules may be alive.
            return False
        # Read all of cpuinfo into a list for data collection
        with open(CPUINFO_PATH, "r") as reader:
            # read first line
            cpuinfo_line = str(reader.readline()).strip()
            # loop until a blank line. This will get us cpu0's config, which is
            # probably plenty.
            while cpuinfo_line != "":
                # Split on colon:
                # model name      : AMD EPYC 7571
                split = cpuinfo_line.split(":")
                # trim leading and trailing whitespace for key and value then
                # reassign since we reference it multiple times. "model name"
                split[0] = split[0].strip()
                split[1] = split[1].strip()
                # cpuinfo_values is a dict, keys are the strings at the start
                # of each /proc/cpuinfo line, value is anything after the colon
                # after some cooking to coerce from strings to proper types and
                # some normalization.
                if split[0] in self.INTEGER_STATS:
                    cpuinfo_values[split[0]] = int(split[1])
                elif split[0] in self.FLOAT_STATS:
                    cpuinfo_values[split[0]] = float(split[1])
                elif split[0] in self.LIST_STATS:
                    # Some entries in cpuinfo have a number of values, such as
                    # "flags"
                    cpuinfo_values[split[0]] = split[1].split()
                else:
                    cpuinfo_values[split[0]] = split[1]

                # Get the next line.
                cpuinfo_line = str(reader.readline()).strip()
        cpuinfo_values["_time"] = time.time()
        return cpuinfo_values

    def GetCpuSoftIrqs(self, cpustats_values):
        logger.debug("Entering GetCpuSoftIrqs")
        if util.caniread(SOFTIRQ_PATH) is False:
            logger.error(f"Fatal: Can't open {SOFTIRQ_PATH} for reading.")
            return False
        with open(SOFTIRQ_PATH, "r") as reader:
            # Get first line
            softirq_line = str(reader.readline()).strip()
            # This is a column-based file for CPUs, so we burn the first line
            # by just reading again. Probably a better way but this works.
            softirq_line = str(reader.readline()).strip()

            while softirq_line != "":
                # Replace colon delimiters with nothing, split on spaces.
                irq = softirq_line.replace(":", "").split()
                # First value is the IRQ "name".
                irqname = irq.pop(0)
                for cpu in cpustats_values.keys():
                    # We have a "cpu" in cpustats_values, but no such value in
                    # softirqs.
                    if cpu.startswith("cpu") and cpu != "cpu":
                        # This should move each value to the correct cpuN,
                        # coercing it to int before assignment.
                        irqval = irq.pop(0)
                        cpustats_values[cpu]["softirqs"][irqname] = int(irqval)
                # Get next line, then return to start of loop
                softirq_line = str(reader.readline()).strip()
        return cpustats_values

    def GetCpuProcStats(self):
        cpustats_values = {}
        cpustats_labels = [
            "user",
            "nice",
            "system",
            "idle",
            "iowait",
            "irq",
            "softirq",
            "steal",
            "guest",
            "guest_nice",
        ]
        if util.caniread(STAT_PATH) is False:
            logger.error(f"Fatal: Can't open {STAT_PATH} for reading.")
            return False
        with open(STAT_PATH, "r") as reader:
            stat_line = str(reader.readline()).strip()
            while stat_line != "":
                if stat_line.startswith("cpu"):
                    split = stat_line.split()
                    # cpu_name is cpu if it's the total metrics for the cpu
                    # it's cpuN for each core/hyperthread
                    cpu_name = split.pop(0)
                    # cpu  545171 4295 203016 140708647 12297 0 6426 232949 0 0
                    # cpu0 272044 2628 100726 70358155 6200 0 3286 102134 0 0
                    # cpu1 273126 1667 102289 70350492 6097 0 3139 130815 0 0
                    cpustats_values[cpu_name] = dict(
                        zip(cpustats_labels, map(int, split))
                    )
                    cpustats_values[cpu_name]["softirqs"] = {}
                elif stat_line.startswith("intr"):
                    # Use this opportunity to get the softirqs for each core
                    # since we should be done with per-cpu stats here.
                    cpustats_values = self.GetCpuSoftIrqs(cpustats_values)
                    # We're not going to deal with the mess of shit that is
                    # the interrupts here.
                    pass

                else:
                    # We split the line, as we always do
                    split = stat_line.split()
                    key = split.pop(0)

                    if key in self.INTEGER_STATS:
                        cpustats_values[key] = int(split[0])
                    elif key in self.FLOAT_STATS:
                        cpustats_values[key] = float(split[0])
                    elif key == "softirq":
                        cpustats_values[key] = list(map(int, split))
                    else:
                        cpustats_values[key] = split
                stat_line = str(reader.readline()).strip()

        cpustats_values["_time"] = time.time()
        return cpustats_values

    def UpdateValues(self):
        logger.debug("CPU: Calling GetCpuinfo()")
        self.cpuinfo_values = self.GetCpuinfo()
        logger.debug("CPU: Calling GetCpuProcStats()")
        self.cpustat_values = self.GetCpuProcStats()

    def __init__(self):
        logger.info("CPU: Initializing CPU Gathering")
        self.UpdateValues()


if __name__ == "__main__":
    import pprint
    import util  # pylint: disable=import-error

    pp = pprint.PrettyPrinter(indent=4)
    mycpu = Cpu()
    pp.pprint(mycpu.cpustat_values)
    pp.pprint(mycpu.cpuinfo_values)
else:
    from . import util
