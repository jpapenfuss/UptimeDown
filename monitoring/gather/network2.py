import socket
import ctypes
import ctypes.util


class s_saddr(ctypes.Structure):
    _fields_ = [
        ("sa_family", ctypes.c_ushort),
        ("sa_data", ctypes.c_byte * 14)
    ]


class s_saddr_in(ctypes.Structure):
    _fields_ = [
        ("sin_family", ctypes.c_ushort),
        ("sin_port", ctypes.c_uint16),
        ("sin_addr", ctypes.c_byte * 4),
    ]


class s_saddr_in6(ctypes.Structure):
    _fields_ = [
        ("sin6_family", ctypes.c_ushort),
        ("sin6_port", ctypes.c_uint16),
        ("sin6_flowinfo", ctypes.c_uint32),
        ("sin6_addr", ctypes.c_byte * 16),
        ("sin6_scope_id", ctypes.c_uint32),
    ]


class union_ifa_ifu(ctypes.Union):
    _fields_ = [
        ("ifu_broadaddr", ctypes.POINTER(s_saddr)),
        ("ifu_dstaddr", ctypes.POINTER(s_saddr)),
    ]


class struct_ifaddrs(ctypes.Structure):
    pass


""" This looks weird, but ifa_next is a pointer back to struct_ifaddrs.
    Since struct_ifaddrs doesn't exist while the class is being defined,
    there's a runtime exception that the class doesn't exist. """
struct_ifaddrs._fields_ = [
    ("ifa_next", ctypes.POINTER(struct_ifaddrs)),
    ("ifa_name", ctypes.c_char_p),
    ("ifa_flags", ctypes.c_uint),
    ("ifa_addr", ctypes.POINTER(s_saddr)),
    ("ifa_netmask", ctypes.POINTER(s_saddr)),
    ("ifa_ifu", union_ifa_ifu),
    ("ifa_data", ctypes.c_void_p),
]

libc = ctypes.CDLL(ctypes.util.find_library("c"))


def ifap_iter(ifap):
    ifa = ifap.contents
    while True:
        yield ifa
        if not ifa.ifa_next:
            break
        ifa = ifa.ifa_next.contents


def getfamaddr(sa):
    family = sa.sa_family
    addr = None
    if family == socket.AF_INET:
        sa = ctypes.cast(ctypes.pointer(sa), ctypes.POINTER(s_saddr_in)).contents
        addr = socket.inet_ntop(family, sa.sin_addr)
    elif family == socket.AF_INET6:
        sa = ctypes.cast(ctypes.pointer(sa), ctypes.POINTER(s_saddr_in6)).contents
        addr = socket.inet_ntop(family, sa.sin6_addr)
    return family, addr


class NetworkInterface(object):
    def __init__(self, name):
        self.name = name
        self.index = libc.if_nametoindex(name)
        self.addresses = {}

    def __str__(self):
        return "%s [index=%d, IPv4=%s, IPv6=%s]" % (
            repr(self.name)[2:-1],
            self.index,
            self.addresses.get(socket.AF_INET),
            self.addresses.get(socket.AF_INET6),
        )


def get_network_interfaces():
    ifap = ctypes.POINTER(struct_ifaddrs)()
    result = libc.getifaddrs(ctypes.pointer(ifap))

    if result != 0:
        raise OSError(ctypes.get_errno())
    del result
    try:
        for ifa in ifap_iter(ifap):
        retval = {}
            name = ifa.ifa_name

            i = retval.get(name)
            if not i:
                i = retval[name] = NetworkInterface(name)
            family, addr = getfamaddr(ifa.ifa_addr.contents)
            if addr:
                i.addresses[family] = addr
        return retval.values()
    finally:
        libc.freeifaddrs(ifap)


if __name__ == "__main__":
    print([str(ni) for ni in get_network_interfaces()])
