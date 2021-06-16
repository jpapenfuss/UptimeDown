import re
import time
import logging

logger = logging.getLogger('monitoring')


class Cpu:

    def GetCpuinfo(self):
        cpuinfo_values = {}
        # Path definitions
        cpuinfo_path = "/proc/cpuinfo"

        # Read all of cpuinfo into a list for data collection
        # We split on a colon, the separator in the file.
        splitter = re.compile('\t*?:\s?')
        with open(cpuinfo_path, 'r') as reader:
            # read first line
            cpuinfo_line = str(reader.readline()).strip()
            # loop until a blank line. This will get us cpu0's config, which is probably plenty.
            while cpuinfo_line != '':
                split = splitter.split(cpuinfo_line)
                cpuinfo_values[split[0]] = split[1]
                cpuinfo_line = str(reader.readline()).strip()

        cpuinfo_values['_time'] = time.time()
        return(cpuinfo_values)

    def GetCpuProcStats(self):
        cpustats_values = {}
        stat_path = "/proc/stat"
        splitter = re.compile('\s+')
        with open(stat_path, 'r') as reader:
            stat_line = str(reader.readline()).strip()
            while stat_line.startswith('cpu'):
                split = splitter.split(stat_line)
                cpu_name = split[0]
                split.pop(0)
                cpustats_values[cpu_name] = {'user': split[0],
                                             'nice': split[1],
                                             'system': split[2],
                                             'idle': split[3],
                                             'iowait': split[4],
                                             'irq': split[5],
                                             'softirq': split[6],
                                             'steal': split[7],
                                             'guest': split[8],
                                             'guest_nice': split[9]}
                stat_line = str(reader.readline()).strip()

            # when we get here, the line after the last cpu* line will be in stat_line. This is interrupts, which
            # we dnn't care about, so we just burn it.
            stat_line = str(reader.readline()).strip()

            # this should be context switches
            split = splitter.split(stat_line)
            cpustats_values[split[0]] = split[1]

            # this should be btime
            stat_line = str(reader.readline()).strip()
            split = splitter.split(stat_line)
            cpustats_values[split[0]] = split[1]

            # this should be processes
            stat_line = str(reader.readline()).strip()
            split = splitter.split(stat_line)
            cpustats_values[split[0]] = split[1]

            # this should be procs_running
            stat_line = str(reader.readline()).strip()
            split = splitter.split(stat_line)
            cpustats_values[split[0]] = split[1]

            # this should be procs_blocked
            stat_line = str(reader.readline()).strip()
            split = splitter.split(stat_line)
            cpustats_values[split[0]] = split[1]
            cpustats_values['_time'] = time.time()
        return(cpustats_values)

    def FindInCpuinfo(searchstring):
        return(self.cpuinfo_values[searchstring])

    def UpdateValues(self):
        self.cpuinfo_values = self.GetCpuinfo()
        self.cpustat_values = self.GetCpuProcStats()

    def __init__(self):
        # We want to get initial data on first instantiation.
        self.UpdateValues()
