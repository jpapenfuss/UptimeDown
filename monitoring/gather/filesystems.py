# https://docs.python.org/3/library/os.html#os.statvfs
# https://man7.org/linux/man-pages/man3/statvfs.3.html

# mount in /proc/mounts:
# /dev/sda2 / ext4 rw,relatime,errors=remount-ro,stripe=128 0 0
# mount in /etc/mtab:
# /dev/sda2 / ext4 rw,relatime,errors=remount-ro,stripe=128 0 0
import logging
import os
import time

lg = logging.getLogger("monitoring")

# os.statvfs_result(f_bsize=4096, f_frsize=4096, f_blocks=0, f_bfree=0,
# f_bavail=0, f_files=0, f_ffree=0, f_favail=0, f_flag=0, f_namemax=255)
STATVFS_KEYS = [
    "f_bsize",
    "f_frsize",
    "f_blocks",
    "f_bfree",
    "f_bavail",
    "f_files",
    "f_ffree",
    "f_favail",
    "f_flag",
    "f_namemax",
]
# A growing list of filesystems to not include when getting fs data
FS_IGNORE = [
    "autofs",
    "bpf",
    "cgroup",
    "cgroup2",
    "configfs",
    "debugfs",
    "devpts",
    "devtmpfs",
    "fusectl",
    "hugetlbfs",
    "mqueue",
    "proc",
    "pstore",
    "securityfs",
    "squashfs",
    "sysfs",
    "tmpfs",
    "tracefs",
    "efivarfs",
    "rpc_pipefs",
    "fuse",
    "binfmt_misc",
    "overlay",
]
MOUNT_KEYS = ["device", "path", "filesystem", "options", "dump", "pass"]


class Filesystems:
    # Can populate this with not-actually-filesystem filesystems.
    # e.g. f_blocks=0
    fs_reject = []
    filesystems = {}

    # Just grabs the available filesystems out of /proc/mounts
    # if /proc/mounts is unreadable tries /etc/mtab, but this
    # will probably spell trouble later.
    def get_filesystems(self):
        mtab_path = "/etc/mtab"
        proc_mounts_path = "/proc/mounts"

        mtab_access = os.access(mtab_path, os.R_OK)
        proc_mounts_access = os.access(proc_mounts_path, os.R_OK)

        if proc_mounts_access is True:
            lg.debug("Can read %s, using that for mounts.", proc_mounts_path)
            filesystems = self.get_filesystems_from_proc(proc_mounts_path)
        elif mtab_access is True:
            # For now we just call the same method, since it's the same format
            # for mtab and proc/mounts
            lg.warning("Failed through from proc, but can read %s, using that for mounts.", mtab_path)
            filesystems = self.get_filesystems_from_proc(mtab_path)
        else:
            lg.error("Fatal: Can't open either %s or %s for reading.", proc_mounts_path, proc_mounts_path)
            exit(1)

        return filesystems

    def explode_options(self, options):
        # Explode initial set of options:
        # options = rw,relatime,noacl,stripe=640,data=ordered,data_err=abort,jqfmt=vfsv0,usrjquota=aquota.user
        myopts = {}
        for opt in options.split(","):
            split_equals = opt.split("=")
            if len(split_equals) == 2:
                if split_equals[1].isdigit():
                    split_equals[1] = int(split_equals[1])
                myopts[split_equals[0]] = split_equals[1]
            else:
                myopts[split_equals[0]] = ""
        return myopts

    def explode_statvfs(self, statvfs):
        fs_stats = {
            "f_bsize": statvfs.f_bsize,
            "f_frsize": statvfs.f_frsize,
            "f_blocks": statvfs.f_blocks,
            "f_bfree": statvfs.f_bfree,
            "f_bavail": statvfs.f_bavail,
            "f_files": statvfs.f_files,
            "f_ffree": statvfs.f_ffree,
            "f_favail": statvfs.f_favail,
            "f_flag": statvfs.f_flag,
            "f_namemax": statvfs.f_namemax
        }
        # If this isn't a real block-based filesystem, return None so the
        # caller can handle this.
        if fs_stats['f_blocks'] == 0:
            return None
        # Total blocks times block size
        fs_stats["bytesTotal"] = fs_stats["f_blocks"] * fs_stats["f_bsize"]
        # Free blocks times block size
        fs_stats["bytesFree"] = fs_stats["f_bfree"] * fs_stats["f_bsize"]
        # Available blocks times block size
        fs_stats["bytesAvailable"] = fs_stats["f_bavail"] * fs_stats["f_bsize"]
        # in theory we shouldn't get a zero in any divisor here, but...
        try:
            fs_stats["pctFree"] = (fs_stats["f_bfree"] / fs_stats["f_blocks"]) * 100
            fs_stats["pctAvailable"] = (fs_stats["f_bavail"] / fs_stats["f_blocks"]) * 100
            fs_stats["pctUsed"] = (1.0 - (fs_stats["f_bfree"] / fs_stats["f_blocks"])) * 100
            fs_stats["pctReserved"] = (1.0 - (fs_stats["f_bavail"] / fs_stats["f_blocks"])) * 100
        except ZeroDivisionError:
            # This shouldn't be possible as results with f_blocks=0 get
            # blacklisted and this never gets called.
            lg.error("DivideByZero for f_blocks, bailing. TODO: Be better.")
            exit(1)
        return fs_stats

    def process_statvfs(self, statvfs):
        fs_stats = {}

        return fs_stats

    def get_filesystems_from_proc(self, proc_mounts_path):
        fs = {}
        with open(proc_mounts_path, "r") as reader:
            # get first line, before the loop.
            mount_line = str(reader.readline()).strip()
            while mount_line != "":
                # split mount_line into a list, whitespace-delimited
                mount = mount_line.split()
                # Each mount entry gets worked:
                # process_mount calls explode_statvfs to get fs usage stats
                # process_mount calls explode_options to get fs mount options
                filesystem = self.process_mount(mount)
                # Can be none if the fs has no blocks - virtual fs of some sort.
                # it gets blacklisted back in explode_statvfs
                if filesystem is not None:
                    # This doesn't handle duplicates. fs is indexed on
                    # mountpoint and there's nothing saying you can't have two
                    # fs mounted on the same mountpoint. It's a dumb mess.
                    fs.update(filesystem)
                # Move on to the next line
                mount_line = str(reader.readline()).strip()
        # Always add a timestamp for identifying when results were captured
        fs["_time"] = time.time()
        return fs

    def process_mount(self, mount):
        # mount[0] is device, 1 is mount path, 2 is filesystem, 3 is
        # options, 4 is dump, 5 is pass.
        # ['/dev/root', '/', 'ext4', 'rw,relatime,discard', '0', '0']
        fs = {}
        if mount[2] not in FS_IGNORE and mount[1] not in self.fs_reject:
            mount[4] = int(mount[4])
            mount[5] = int(mount[5])
            fs[mount[1]] = dict(zip(MOUNT_KEYS, mount))
            fs[mount[1]]["fs_stats"] = self.explode_statvfs(os.statvfs(mount[1]))
            # Now that we took the time to parse the filesystem details
            # check to see if it is actually a real filesystem
            # (currently determined by f_blocks not being zero)
            if fs[mount[1]]["fs_stats"] is None:
                self.fs_reject.append(mount[1])
                return None
            else:
                # And then we do the math to get more useful values
                fs[mount[1]]["options"] = self.explode_options(mount[3])
        return fs

    def __init__(self):
        self.filesystems = self.get_filesystems()


if __name__ == "__main__":
    myfilesystems = Filesystems()
    import pprint

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(myfilesystems.filesystems)
