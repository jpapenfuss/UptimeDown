# https://docs.python.org/3/library/os.html#os.statvfs
# https://man7.org/linux/man-pages/man3/statvfs.3.html

# mount in /proc/mounts: /dev/sda2 / ext4 rw,relatime,errors=remount-ro,stripe=128 0 0
# mount in /etc/mtab:    /dev/sda2 / ext4 rw,relatime,errors=remount-ro,stripe=128 0 0
import logging
import os
import re
import pprint

pp = pprint.PrettyPrinter(indent=4)
logger = logging.getLogger('monitoring')

# os.statvfs_result(f_bsize=4096, f_frsize=4096, f_blocks=0, f_bfree=0,
# f_bavail=0, f_files=0, f_ffree=0, f_favail=0, f_flag=0, f_namemax=255)
STATVFS_KEYS = ['f_bsize', 'f_frsize', 'f_blocks', 'f_bfree',
                'f_bavail', 'f_files', 'f_ffree', 'f_favail', 'f_flag', 'f_namemax']

FS_IGNORE = ['autofs', 'bpf', 'cgroup', 'cgroup2', 'configfs', 'debugfs', 'devpts', 'devtmpfs', 'fusectl', 'hugetlbfs', 'mqueue',
             'proc', 'pstore', 'securityfs', 'squashfs', 'sysfs', 'tmpfs', 'tracefs', 'efivarfs', 'rpc_pipefs', 'fuse', 'binfmt_misc']

MOUNT_KEYS = ['device', 'path', 'filesystem', 'options', 'dump', 'pass']

# Can populate this with not-actually-filesystem filesystems. e.g. f_blocks=0


class Filesystems:
    fs_reject = []
    filesystems = {}

    def GetFilesystems(self):
        mtab_path = '/etc/mtab'
        proc_mounts_path = '/proc/mounts'

        mtab_access = os.access(mtab_path, os.R_OK)
        proc_mounts_access = os.access(proc_mounts_path, os.R_OK)

        if proc_mounts_access == True:
            logger.debug(
                f'Can read {proc_mounts_path}, using that for mounts.')
            filesystems = self.GetFilesystemsFromProc(proc_mounts_path)
        elif mtab_access == True:
            # For now we just call the same method, since it's the same format for mtab and proc/mounts
            filesystems = self.GetFilesystemsFromProc(mtab_path)
        else:
            logger.error(
                f"Fatal: Can't open either {mtab_path} or {proc_mounts_path} for reading.")
            exit(1)

        return(filesystems)

    def ExplodeStatvfs(self, statvfs):

        # This is so stupid. But it works. For each iterable value in statvfs, populate a dict that would
        # have a numeric index for each k>v pair, then get the values of the k>v pairs. Then we zip with
        # the list of keys. Yes. Fucking dumb.
        statvfs_values = list(dict(enumerate(statvfs)).values())
        stats = dict(zip(STATVFS_KEYS, statvfs_values))
        return(stats)

    def ProcessStatvfs(self, statvfs):
        fs_stats = {}
        # Total blocks times block size
        fs_stats['bytesTotal'] = statvfs['f_blocks'] * statvfs['f_bsize']
        # Free blocks times block size
        fs_stats['bytesFree'] = statvfs['f_bfree'] * statvfs['f_bsize']
        # Available blocks times block size
        fs_stats['bytesAvailable'] = statvfs['f_bavail'] * statvfs['f_bsize']
        # blocks free times block size.
        # TODO: Investigate a relatively large delta on my nVME raid.
        # Maybe this relates to trim? It was a pretty large discrepancy.
        fs_stats['bytesFree'] = statvfs['f_bfree'] * statvfs['f_bsize']
        # in theory we shouldn't get a zero in any divisor here, but...
        try:
            fs_stats['pctFree'] = statvfs['f_bfree'] / statvfs['f_blocks']
            fs_stats['pctAvailable'] = statvfs['f_bavail'] / \
                statvfs['f_blocks']
            fs_stats['pctUsed'] = 1.0 - \
                (statvfs['f_bfree'] / statvfs['f_blocks'])
            fs_stats['pctReserved'] = 1.0 - \
                (statvfs['f_bavail'] / statvfs['f_blocks'])
        except ZeroDivisionError:
            logger.error(
                'DivideByZero for f_blocks, bailing. TODO: Be better.')
            exit(1)

        return(fs_stats)

    def GetFilesystemsFromProc(self, proc_mounts_path):
        fs = {}
        with open(proc_mounts_path, 'r') as reader:
            splitter = re.compile('\s')

            # get first line, before the loop.
            mount_line = str(reader.readline()).strip()
            while mount_line != '':
                mount = splitter.split(mount_line)
                if mount[2] not in FS_IGNORE and mount[1] not in self.fs_reject:
                    fs[mount[1]] = dict(zip(MOUNT_KEYS, mount))
                    fs[mount[1]]['vfstats'] = self.ExplodeStatvfs(
                        os.statvfs(mount[1]))

                    # Now that we took the time to parse the filesystem details, check to see if it is actually
                    # a real filesystem (currently determined by f_blocks not being zero)
                    if fs[mount[1]]['vfstats']['f_blocks'] == 0:
                        fs.pop(mount[1])
                        self.fs_reject.append(mount[1])
                    else:
                        # And then we do the math to get more useful values
                        fs[mount[1]]['fs_stats'] = self.ProcessStatvfs(
                            fs[mount[1]]['vfstats'])

                # Move on to the next line
                mount_line = str(reader.readline()).strip()
        return(fs)

    def __init__(self):
        self.filesystems = self.GetFilesystems()


if __name__ == "__main__":
    myfilesystems = Filesystems()
    pp.pprint(myfilesystems.filesystems)
