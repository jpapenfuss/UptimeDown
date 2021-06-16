import re
import time
import os
import sys
import logging

logger = logging.getLogger('monitoring')


class Memory:

    def GetMeminfo(self):
        # Path definitions
        meminfo_path = "/proc/meminfo"
        meminfo_values = {}

        if os.access(meminfo_path, os.R_OK) == False:
            logger.error(f"Fatal: Can't open {meminfo_path} for reading.")
            exit(1)
        # Read all of cpuinfo into a list for data collection
        with open(meminfo_path, 'r') as reader:
            stripper = re.compile('(:)?\s+')
            splitter = re.compile('\s')
            # read in first line
            meminfo_line = str(reader.readline()).strip()
            # Iterate until EOF
            while meminfo_line != '':
                # Substitutes the regex compiled as stripper.sub for single-spaces
                line = stripper.sub(' ', meminfo_line, count=0)
                # Split on single space
                line = splitter.split(line)
                # coerce second value into int, it should only ever be a number
                line[1] = int(line[1])

                # If we have 3 values, it's Key:Value:Multiplier (kB/mB/gB)
                # I have no idea if the multiplier can be anything but kB but...
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
        meminfo_values['_time'] = time.time()
        return(meminfo_values)

    def FindInMeminfo(self, searchstring):
        return(self.meminfo_values[searchstring])

    def __init__(self):
        logger.info('Initializing Memory Gathering')
        # On instantiation, get meminfo. We'll also call GetMemInfo on updates.
        self.meminfo_values = self.GetMeminfo()
