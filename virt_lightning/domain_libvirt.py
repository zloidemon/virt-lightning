import asyncio
import ipaddress
import logging
import re
import string
from xml.etree import ElementTree

import libvirt

import virt_lightning.consts as consts

DISK_XML = """
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source />
      <target bus='virtio'/>
    </disk>
"""

BRIDGE_XML = """
<interface type='network'>
  <source network='virt-lightning'/>
  <model type='virtio'/>
</interface>
"""

logger = logging.getLogger("virt_lightning")


class LibvirtDomain:
    def __init__(self, dom):
        self.dom = dom
        self.user_data = {
            "resize_rootfs": True,
            "disable_root": 0,
            "bootcmd": [],
            "runcmd": [],
        }
        self._ssh_key = None
        self.default_nic_model = None
        self.nics = []
        self.meta_data_media_type = None
        self.default_bus_type = None

    @property
    def root_password(self):
        return self.get_metadata("root_password")

    @root_password.setter
    def root_password(self, value):
        self.user_data["disable_root"] = False
        self.user_data["password"] = value
        self.user_data["chpasswd"] = {
            "list": f"root:{value}\n",
            "expire": False,
        }
        self.user_data["ssh_pwauth"] = True
        self.record_metadata("root_password", value)

    @property
    def ssh_key(self):
        return self._ssh_key

    @ssh_key.setter
    def ssh_key(self, value):
        self._ssh_key = value

    def load_ssh_key_file(self, ssh_key_file):
        doc_url = "https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/#generating-a-new-ssh-key"
        try:
            self.ssh_key = ssh_key_file.expanduser().read_text()
        except OSError:
            logger.error(
                f"Can not read {ssh_key_file}. If you don't have any SSH key, "
                f"please follow the steps describe here:\n  {doc_url}"
            )
            raise

        self.user_data["ssh_authorized_keys"] = [self.ssh_key]
        if "users" in self.user_data:
            self.user_data["users"][0]["ssh_authorized_keys"] = [self.ssh_key]

    @property
    def distro(self):
        return self.get_metadata("distro")

    @distro.setter
    def distro(self, distro):
        self.record_metadata("distro", distro)

    @property
    def python_interpreter(self):
        return self.get_metadata("python_interpreter")

    @python_interpreter.setter
    def python_interpreter(self, value):
        self.record_metadata("python_interpreter", value)

    @property
    def username(self):
        return self.get_metadata("username")

    @username.setter
    def username(self, username):
        if not re.match(consts.RE_USERNAME_PATTERN, username):
            raise Exception("Invalid username: ", username)

        self.user_data["users"] = [
            {
                "name": username,
                "gecos": "virt-bootstrap user",
                "sudo": "ALL=(ALL) NOPASSWD:ALL",
                "ssh_authorized_keys": [self.ssh_key],
            }
        ]

        self.record_metadata("username", username)

    @property
    def name(self):
        return self.dom.name()

    @name.setter
    def name(self, name):
        self.user_data["name"] = name
        self.dom.rename(name, 0)

    @property
    def fqdn(self):
        return self.get_metadata("fqdn")

    @fqdn.setter
    def fqdn(self, value):
        fqdn_validate = re.compile(consts.RE_FQDN_PATTERN, re.IGNORECASE)
        if not value or not fqdn_validate.match(value):
            logger.error(f"Invalid FQDN: {value}")
            return
        self.user_data["fqdn"] = value
        self.record_metadata("fqdn", value)

    @property
    def vcpus(self):
        xml = self.dom.XMLDesc(0)
        root = ElementTree.fromstring(xml)
        vcpu = root.findall("./vcpu")[0]
        return int(vcpu.attrib.get("current", vcpu.text))

    @vcpus.setter
    def vcpus(self, value=1):
        self.dom.setVcpusFlags(value, libvirt.VIR_DOMAIN_AFFECT_CONFIG)

    @property
    def memory(self):
        xml = self.dom.XMLDesc(0)
        root = ElementTree.fromstring(xml)
        memory = root.findall("./memory")[0]
        unit = memory.attrib["unit"]

        if unit == "KiB":
            return int(int(memory.text) / 1024)
        elif unit == "MiB":
            return int(int(memory.text))

    @memory.setter
    def memory(self, value):
        if value < 256:
            logger.warning(f"low memory: {value}MB for VM {self.name}")
        value *= 1024
        self.dom.setMemoryFlags(
            value, libvirt.VIR_DOMAIN_AFFECT_CONFIG | libvirt.VIR_DOMAIN_MEM_MAXIMUM
        )
        self.dom.setMemoryFlags(value, libvirt.VIR_DOMAIN_AFFECT_CONFIG)

    def get_next_block_device(self):
        if not hasattr(self, "blockdev"):
            self.blockdev = list(string.ascii_lowercase)
            self.blockdev.reverse()
        return f"vd{self.blockdev.pop()}"

    def record_metadata(self, k, v):
        meta = f"<{k} name='{v}' />"
        self.dom.setMetadata(
            libvirt.VIR_DOMAIN_METADATA_ELEMENT,
            meta,
            "vl",
            k,
            libvirt.VIR_DOMAIN_AFFECT_CONFIG,
        )

    def get_metadata(self, k):
        try:
            xml = self.dom.metadata(libvirt.VIR_DOMAIN_METADATA_ELEMENT, k)
        except libvirt.libvirtError as e:
            if e.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN_METADATA:
                return None
            raise (e)
        elt = ElementTree.fromstring(xml)
        return elt.attrib["name"]

    @property
    def context(self):
        return self.get_metadata("context")

    @context.setter
    def context(self, value):
        self.record_metadata("context", value)

    @property
    def groups(self):
        value = self.get_metadata("groups")
        if not value:
            return []
        return value.split(",")

    @groups.setter
    def groups(self, value):
        self.record_metadata("groups", ",".join(value))

    def attach_disk(self, volume, device="disk", disk_type="qcow2"):
        if device == "cdrom":  # noqa: SIM108
            # virtio does not support ejectable media
            bus = "ide"
        else:
            bus = self.default_bus_type or "virtio"

        device_name = self.get_next_block_device()
        disk_root = ElementTree.fromstring(DISK_XML)
        disk_root.attrib["device"] = device
        disk_root.findall("./driver")[0].attrib = {"name": "qemu", "type": disk_type}
        disk_root.findall("./source")[0].attrib = {"file": volume.path()}
        disk_root.findall("./target")[0].attrib = {"dev": device_name, "bus": bus}
        xml = ElementTree.tostring(disk_root).decode()
        self.dom.attachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        return device_name

    def attach_network(
        self,
        network=None,
        nic_model=None,
        ipv4=None,
        mac=None,
        bridge=None,
        virtualport_type=None,
    ):
        if not nic_model:
            nic_model = self.default_nic_model
        net_root = ElementTree.fromstring(BRIDGE_XML)

        if bridge:
            source_attrs = {"bridge": bridge}
            net_root.attrib["type"] = "bridge"
        elif network:
            source_attrs = {"network": network}
        net_root.findall("./source")[0].attrib = source_attrs
        net_root.findall("./model")[0].attrib = {"type": nic_model}

        if virtualport_type:
            net_root.append(ElementTree.Element("virtualport", type=virtualport_type))

        if mac:
            mac_el = ElementTree.SubElement(net_root, "mac")
            mac_el.attrib = {"address": mac}

        if not ipv4:
            if not self.nics:
                raise ValueError("First NIC should have a static IPv4 address.")
            ipv4_instance = None  # DHCP
        elif isinstance(ipv4, ipaddress.IPv4Interface):
            ipv4_instance = ipv4
        elif ipv4 and "/" not in ipv4:
            ipv4_instance = ipaddress.IPv4Interface(ipv4 + "/24")
        elif ipv4:
            ipv4_instance = ipaddress.IPv4Interface(ipv4)
        self.nics.append({"network": network, "ipv4": ipv4_instance})

        self.ipv4 = self.nics[0]["ipv4"]

        xml = ElementTree.tostring(net_root).decode()
        self.dom.attachDeviceFlags(xml, libvirt.VIR_DOMAIN_AFFECT_CONFIG)

        xml = self.dom.XMLDesc(0)
        root = ElementTree.fromstring(xml)
        ifaces = root.findall("./devices/interface/mac[@address]")
        for i, iface in enumerate(ifaces):
            self.nics[i]["mac"] = iface.attrib["address"]

    def add_root_disk(self, root_disk_path):
        self.attach_disk(root_disk_path)

    @property
    def ipv4(self):
        if self.get_metadata("ipv4"):
            return ipaddress.IPv4Interface(self.get_metadata("ipv4"))

    @ipv4.setter
    def ipv4(self, value):
        self.record_metadata("ipv4", value)

    @property
    def bootcmd(self):
        return self.user_data["bootcmd"]

    @bootcmd.setter
    def bootcmd(self, value):
        if not hasattr(value, "append"):
            raise ValueError("bootcmd should be a list of command")
        self.user_data["bootcmd"] = value

    @property
    def runcmd(self):
        return self.user_data["runcmd"]

    @runcmd.setter
    def runcmd(self, value):
        if not hasattr(value, "append"):
            raise ValueError("runcmd should be a list of command")
        self.user_data["runcmd"] = value

    def set_user_password(self, user, password):
        return self.dom.setUserPassword(user, password)

    def __gt__(self, other):
        return self.name > other.name

    def __lt__(self, other):
        return self.name < other.name

    async def reachable(self):
        while True:
            try:
                reader, _ = await asyncio.open_connection(str(self.ipv4.ip), 22)
                data = await reader.read(10)
                if data.decode().startswith("SSH"):
                    logger.info(f"+ {self.name} found at {self.ipv4.ip}!")
                    return
            except OSError:
                pass
