#I wanted to manually get network interface details, but the work to get it is... Unappealing, via ctypes and interfacing with glibc. I'll do it later. This is a minor dependency.
import netifaces
import logging

logger = logging.getLogger("monitoring")


class Interfaces:
    skip_loopback = False
    network = {"gateways": [], "interfaces": []}

    def GetInterfaces(self):
        ifaces_with_ips = {}
        ifaces = netifaces.interfaces()
        if self.skip_loopback is True:
            try:
                ifaces.pop(ifaces.index("lo"))
            except:
                pass
        for iface in ifaces:
            # ifaddresses is keyed on net family, print(netifaces.address_families). Most important.common:
            # 2: 'AF_INET', 10: 'AF_INET6', 17: 'AF_PACKET',
            ifaces_with_ips[iface] = netifaces.ifaddresses(iface)

            if util.caniread("/sys/class/net/", )

        """ returns:
        {'interfaces':{
            'ens5':{
                2:  [   {'addr': '10.0.2.39', 'broadcast': '10.0.2.255', 'netmask': '255.255.255.0' }],
                10: [   {'addr': '2600:1f14:ea6:5d02:c2ec:97c7:2e8b:2452', 'netmask': 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'},
                        {'addr': 'fe80::4bd:e2ff:fecd:e4fb%ens5','netmask': 'ffff:ffff:ffff:ffff::'}],
                17: [   {'addr': '06:bd:e2:cd:e4:fb','broadcast': 'ff:ff:ff:ff:ff:ff'}]},
            'lo':{
                2:  [   {'addr': '127.0.0.1','netmask': '255.0.0.0', 'peer': '127.0.0.1'}],
                10: [   {'addr': '::1','netmask': 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'}],
                17: [   {'addr': '00:00:00:00:00:00','peer': '00:00:00:00:00:00'}]
            }
        }}
        """
        return ifaces_with_ips

    def GetGateways(self):
        gateways = netifaces.gateways()
        ''' Returns:
        {'gateways': {
            2:  [('10.0.2.1', 'ens5', True)],
            10: [('fe80::4fb:7bff:fec9:be06', 'ens5', True)],
            'default': { 2: ('10.0.2.1', 'ens5'), 10: ('fe80::4fb:7bff:fec9:be06', 'ens5') }
        }}
        '''
        return gateways

    def UpdateValues(self):
        logger.debug("Interfaces: Calling GetInterfaces()")
        self.network["interfaces"] = self.GetInterfaces()
        logger.debug("Interfaces: Calling GetGateways()")
        self.network["gateways"] = self.GetGateways()

    def __init__(self):
        logger.info("Interfaces: Initializing Interface Gathering")
        self.UpdateValues()


if __name__ == "__main__":
    import pprint

    import util  # pylint: disable=import-error

    pp = pprint.PrettyPrinter(indent=4)
    myInterfaces = Interfaces()
    pp.pprint(myInterfaces.network)
else:
    from . import util
    pass
