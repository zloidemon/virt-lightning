import logging
import pathlib
import uuid
from xml.etree import ElementTree

import libvirt

from virt_lightning.consts import (
    DEFAULT_DOMAIN_CONFIGURATION,
    DEFAULT_LOGGER,
    ExitCode,
)
from virt_lightning.disk_auxiliary_cloudinit import AuxiliaryCloudInitDisk
from virt_lightning.disk_auxiliary_ignition import AuxiliaryIgnitionDisk
from virt_lightning.disk_auxiliary_openstack import AuxiliaryOpenstackInitDisk
from virt_lightning.domain_libvirt import LibvirtDomain
from virt_lightning.execfile_virtualization_tools import ExecFileVirtTool
from virt_lightning.network_system import NetworkSystem
from virt_lightning.storage_system import StorageSystem

DOMAIN_XML = """
<domain type='kvm'>
  <name></name>
  <memory unit='KiB'>786432</memory>
  <currentMemory unit='KiB'>786432</currentMemory>
  <vcpu>2</vcpu>
  <os>
    <type arch='x86_64' machine='pc'>hvm</type>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
    <vmport state='off'/>
  </features>
  <cpu mode='host-model' check='partial'>
    <model fallback='allow'/>
  </cpu>
  <clock offset='utc'>
    <timer name='rtc' tickpolicy='catchup'/>
    <timer name='pit' tickpolicy='delay'/>
    <timer name='hpet' present='no'/>
  </clock>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>destroy</on_crash>
  <pm>
    <suspend-to-mem enabled='no'/>
    <suspend-to-disk enabled='no'/>
  </pm>
  <devices>
    <emulator>/usr/bin/qemu-kvm</emulator>
    <controller type='usb'></controller>
    <controller type='pci' model='pci-root'/>
    <console type='pty'>
      <target type='serial'/>
    </console>
    <console type='pty'>
      <target type='virtio'/>
    </console>
    <channel type='unix'>
      <target type='virtio' name='org.qemu.guest_agent.0' state='connected'/>
    </channel>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    <graphics type="vnc" port="-1" autoport="yes" listen="127.0.0.1" keymap="en-us">
      <listen type="address" address="127.0.0.1"/>
    </graphics>
    <memballoon model='virtio'></memballoon>
  </devices>
</domain>
"""

logger = logging.getLogger(DEFAULT_LOGGER)


class VMMLibvirt:
    def __init__(self, conn):
        if conn is None:
            logger.error("Failed to open connection to libvirt")
            exit(ExitCode.FAIL.value)

        self.conn = conn
        self.network = NetworkSystem(conn)
        self.storage = StorageSystem(conn)

    @property
    def arch(self):
        caps = self.conn.getCapabilities()
        root = ElementTree.fromstring(caps)
        return root.find("./host/cpu/arch").text

    @property
    def domain_type(self):
        caps = self.conn.getCapabilities()
        root = ElementTree.fromstring(caps)
        available = [
            e.attrib["type"] for e in root.findall("./guest/arch/domain[@type]")
        ]
        if not available:
            raise Exception("No domain type available!")
        if "kvm" not in available:
            logger.warning("kvm mode not available!")
        # Sorted to get kvm before qemu, assume there is no other type
        return sorted(available)[0]

    def create_domain(self, name=None, distro=None):
        if not name:
            name = uuid.uuid4().hex[0:10]
        root = ElementTree.fromstring(DOMAIN_XML)
        root.attrib["type"] = self.domain_type
        root.find("./name").text = name
        root.find("./vcpu").text = str(self.conn.getInfo()[2])
        root.find("./devices/emulator").text = str(ExecFileVirtTool().entrypoint)
        root.find("./os/type").attrib["arch"] = self.arch
        dom = self.conn.defineXML(ElementTree.tostring(root).decode())
        domain = LibvirtDomain(dom)
        domain.distro = distro
        return domain

    def configure_domain(self, domain, user_config):
        config = DEFAULT_DOMAIN_CONFIGURATION
        #
        # NOTE: Перезапись конфигурации поставляемой к образу
        #
        for k, v in self.storage.get_distro_configuration(domain.distro).items():
            if v:
                config[k] = v
        for k, v in user_config.items():
            if v:
                config[k] = v
        domain.groups = config["groups"]
        domain.load_ssh_key_file(pathlib.Path(config["ssh_key_file"]))
        domain.memory = config["memory"]
        domain.root_password = config["root_password"]
        domain.username = config["username"]
        domain.vcpus = config["vcpus"]
        domain.default_nic_model = config["default_nic_model"]
        domain.bootcmd = config["bootcmd"]
        domain.runcmd = config["runcmd"]
        domain.meta_data_media_type = config["meta_data_media_type"]
        domain.default_bus_type = config["default_bus_type"]
        if "fqdn" in config:
            domain.fqdn = config["fqdn"]

    def list_domains(self):
        for domain in self.conn.listAllDomains():
            yield LibvirtDomain(domain)

    def get_domain_by_name(self, name):
        try:
            dom = self.conn.lookupByName(name)
            return LibvirtDomain(dom)
        except libvirt.libvirtError as e:
            if e.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN:
                return None
            else:
                raise

    def start(self, domain, metadata_format):
        cloud_init_iso, init_builder = None, None
        if metadata_format.get("provider", "") == "nocloud" or domain.distro.startswith(
            "centos-6"
        ):
            init_builder = AuxiliaryCloudInitDisk
        elif domain.distro.startswith("coreos"):
            init_builder = AuxiliaryIgnitionDisk
        else:
            #
            # NOTE: OpenStack format is the default
            #
            init_builder = AuxiliaryOpenstackInitDisk

        if init_builder:
            cloud_init_iso = init_builder(self.conn, self.storage, self.network).init(
                domain
            )
            media_type = domain.meta_data_media_type
            domain.attach_disk(cloud_init_iso, device=media_type, disk_type="raw")

        domain.dom.create()
        self.network.remove_domain_from_network(domain)
        self.add_domain_to_network(domain)

    def add_domain_to_network(self, domain):
        self.network.set_dns_entry(domain.ipv4, [domain.name, domain.fqdn])
        self.network.set_dhcp_entry(domain.ipv4, domain.nics[0]["mac"])

    def clean_up(self, domain):
        self.network.remove_domain_from_network(domain)
        xml = domain.dom.XMLDesc(0)
        state, _ = domain.dom.state()
        if state != libvirt.VIR_DOMAIN_SHUTOFF:
            domain.dom.destroy()
        flag = libvirt.VIR_DOMAIN_UNDEFINE_MANAGED_SAVE
        flag |= libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA
        domain.dom.undefineFlags(flag)

        self.storage.storage_pool_obj.refresh()
        root = ElementTree.fromstring(xml)
        for disk in root.findall("./devices/disk[@type='file']/source[@file]"):
            filepath = pathlib.PosixPath(disk.attrib["file"])
            if filepath.exists():
                logger.debug("Purge volume: %s", str(filepath))
                vol = self.storage.storage_pool_obj.storageVolLookupByName(
                    filepath.name
                )
                vol.delete()
