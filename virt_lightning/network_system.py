import ipaddress
import logging
from xml.etree import ElementTree

import libvirt

from virt_lightning.consts import DEFAULT_LOGGER, ExitCode

logger = logging.getLogger(DEFAULT_LOGGER)


NETWORK_DHCP_ENTRY = """
<host />
"""

NETWORK_HOST_ENTRY = """
<host ip="">
</host>"""

NETWORK_XML = """
<network>
  <name></name>
  <forward mode='nat'/>
  <bridge name='virbr0' stp='off' delay='0'/>
  <ip address='192.168.123.1' netmask='255.255.255.0'>
  <dhcp>
    <leasetime>10s</leasetime>
  </dhcp>
  </ip>
</network>
"""


class NetworkSystem:
    def __init__(self, conn):
        self._last_free_ipv4 = None
        self.conn = conn
        self.dns = None
        self.gateway = None
        self.network = None
        self.network_obj = None

    def __get_network_by_name(self, network_name):
        try:
            return self.conn.networkLookupByName(network_name)
        except libvirt.libvirtError as e:
            if e.get_error_code() != libvirt.VIR_ERR_NO_NETWORK:
                raise (e)

    def __create_network(self, network_name, network_cidr):
        network = ipaddress.ip_network(network_cidr)
        root = ElementTree.fromstring(NETWORK_XML)
        root.find("./name").text = network_name
        root.find("./bridge").attrib["name"] = network_name
        root.find("./ip").attrib = {
            "address": network[1].exploded,
            "netmask": network.netmask.exploded,
        }
        xml = ElementTree.tostring(root).decode()

        try:
            return self.conn.networkCreateXML(xml)
        except libvirt.libvirtError as e:
            logger.error(
                "Failed to create network '%s' (CIDR: %s): %s",
                network_name,
                network_cidr,
                e,
            )
            exit(ExitCode.FAIL)

    def reuse_mac_address(self, network_name, domain_name, ipv4):
        network_obj = self.__get_network_by_name(network_name)
        for lease in network_obj.DHCPLeases():
            if lease["hostname"] == domain_name and lease["ipaddr"] == str(ipv4.ip):
                return lease["mac"]

    def set_dhcp_entry(self, ipv4, mac=None):
        root = ElementTree.fromstring(NETWORK_DHCP_ENTRY)
        root.attrib["mac"] = mac
        root.attrib["ip"] = str(ipv4.ip)
        xml = ElementTree.tostring(root).decode()
        self.network_obj.update(
            libvirt.VIR_NETWORK_UPDATE_COMMAND_ADD_FIRST,
            libvirt.VIR_NETWORK_SECTION_IP_DHCP_HOST,
            0,
            xml,
            libvirt.VIR_NETWORK_UPDATE_AFFECT_LIVE,
        )

    def set_dns_entry(self, ipv4, names=None):
        root = ElementTree.fromstring(NETWORK_HOST_ENTRY)
        for name in names:
            if name:
                ElementTree.SubElement(root, "hostname").text = name
        root.attrib["ip"] = str(ipv4.ip)
        xml = ElementTree.tostring(root).decode()
        self.network_obj.update(
            libvirt.VIR_NETWORK_UPDATE_COMMAND_ADD_FIRST,
            libvirt.VIR_NETWORK_SECTION_DNS_HOST,
            0,
            xml,
            libvirt.VIR_NETWORK_UPDATE_AFFECT_LIVE,
        )

    def init_network(self, network_name, network_cidr):
        try:
            self.network_obj = self.conn.networkLookupByName(network_name)
        except libvirt.libvirtError as e:
            if e.get_error_code() != libvirt.VIR_ERR_NO_NETWORK:
                raise (e)

        if not self.network_obj:
            self.network_obj = self.__create_network(network_name, network_cidr)

        if not self.network_obj.isActive():
            self.network_obj.create()
        self.gateway = self.get_network_gateway(network_name)
        self.dns = self.gateway
        self.network = self.gateway.network

    def get_network_gateway(self, network_name):
        network_obj = self.__get_network_by_name(network_name)
        xml = network_obj.XMLDesc(0)
        root = ElementTree.fromstring(xml)
        ip = root.find("./ip")
        return ipaddress.IPv4Interface("{address}/{netmask}".format(**ip.attrib))

    def get_free_ipv4(self, domains):
        used_ips = [self.gateway]
        for dom in domains:
            ipstr = dom.get_metadata("ipv4")
            if not ipstr:
                continue
            interface = ipaddress.ip_interface(ipstr)
            used_ips.append(interface)

        for ip in self.network:
            cidr_ip = f"{ip}/24"
            interface = ipaddress.IPv4Interface(cidr_ip)
            if int(interface.ip.exploded.split(".")[3]) < 5:
                continue
            if self._last_free_ipv4 and self._last_free_ipv4 >= interface:
                continue
            if interface.ip not in [i.ip for i in used_ips]:
                self._last_free_ipv4 = interface
                return interface

    def remove_domain_from_network(self, domain):
        root = ElementTree.fromstring(self.network_obj.XMLDesc(0))
        if not domain.ipv4:
            return
        for host in root.findall("./dns/host[@ip]"):
            if host.attrib["ip"] != str(domain.ipv4.ip):
                continue
            xml = ElementTree.tostring(host, encoding="unicode")
            self.network_obj.update(
                libvirt.VIR_NETWORK_UPDATE_COMMAND_DELETE,
                libvirt.VIR_NETWORK_SECTION_DNS_HOST,
                0,
                xml,
                libvirt.VIR_NETWORK_UPDATE_AFFECT_LIVE,
            )

        root = ElementTree.fromstring(self.network_obj.XMLDesc(0))
        for host in root.findall("./ip/dhcp/host[@ip]"):
            if host.attrib["ip"] != str(domain.ipv4.ip):
                continue
            xml = ElementTree.tostring(host, encoding="unicode")
            self.network_obj.update(
                libvirt.VIR_NETWORK_UPDATE_COMMAND_DELETE,
                libvirt.VIR_NETWORK_SECTION_IP_DHCP_HOST,
                0,
                xml,
                libvirt.VIR_NETWORK_UPDATE_AFFECT_LIVE,
            )

        domain_root = ElementTree.fromstring(domain.dom.XMLDesc(0))
        ifaces = domain_root.findall("./devices/interface/mac[@address]")
        domain_macs = [iface.attrib["address"] for iface in ifaces]

        root = ElementTree.fromstring(self.network_obj.XMLDesc(0))
        for host in root.findall("./ip/dhcp/host[@mac]"):
            if host.attrib["mac"] not in domain_macs:
                continue
            xml = ElementTree.tostring(host, encoding="unicode")
            self.network_obj.update(
                libvirt.VIR_NETWORK_UPDATE_COMMAND_DELETE,
                libvirt.VIR_NETWORK_SECTION_IP_DHCP_HOST,
                0,
                xml,
                libvirt.VIR_NETWORK_UPDATE_AFFECT_LIVE,
            )
