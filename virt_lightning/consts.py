from enum import Enum, unique


@unique
class LoginMethod(Enum):
    SSH = "ssh"


@unique
class ExitCode(Enum):
    OK = 0
    FAIL = 1


CLI_MESSAGE_HELP = """
Example:

 We export the list of the distro in the {conf} file.
   $ {cli} images > {conf}

 For each line of the {conf}, start a VM with the associated distro.
   $ {cli} up

 Once the VM are up, we can generate an Ansible inventory file:
   $ {cli} ansible inventory

 The file is ready to be used by Ansible:
   $ ansible all -m ping -i inventory

Commands:
    up                  Start VMs defined in {conf}
    down                Delete all VMs created by app
    start               Start a new VM
    stop                Delete a VM
    images              Dump list of supported distros
    storage             Dump the VM image storage directory
    ansible             Ansible commands
    ssh                 SSH into VM
    console             Open console on a VM
    viewer              Open VM with virt-viewer
    ps                  Get list of running VM's
    config              Dump configuration
"""
CLI_MESSAGE_USAGE = """
usage: {cli} [--debug DEBUG] [--config CONFIG] COMMAND

Run {cli} without a command to see list of accepted commands.
"""
DEFAULT_VL_NAME = "virt-lightning"
DEFAULT_VL_COMMAND = "vl"
DEFAULT_LOGGER = DEFAULT_VL_NAME.replace("-", "_")
DEFAULT_VL_CONFIGURATION_FILE = DEFAULT_VL_NAME + ".toml"
DEFAULT_BASE_REGISTRY_URL = "http://localhost"
DEFAULT_CONFIGFILE = f"~/.config/{DEFAULT_VL_NAME}/config.ini"
DEFAULT_USER_USERNAME = "root"
DEFAULT_USER_PASSWORD = "root"
DEFAULT_CONFIGURATION = {
    "main": {
        "libvirt_uri": "qemu:///system",
        "root_password": DEFAULT_USER_PASSWORD,
        "storage_pool": f"{DEFAULT_VL_NAME}",
        "network_name": f"{DEFAULT_VL_NAME}",
        "network_cidr": "192.168.123.0/24",
        "network_auto_clean_up": True,
        "ssh_key_file": "~/.ssh/id_rsa.pub",
        "registry_urls": "",
    }
}
DEFAULT_LIBVIRT_GROUP = "libvirt"
DEFAULT_STORAGE_DIR = f"/var/lib/{DEFAULT_VL_NAME}/pool"
EXEC_FILE_GENISOIMAGE = "genisoimage"
EXEC_FILE_KVM = "kvm"
EXEC_FILE_MKISOFS = "mkisofs"
EXEC_FILE_MKPASSWD = "mkpasswd"
EXEC_FILE_QEMU_IMG = "qemu-img"
EXEC_FILE_QEMU_KVM = "qemu-kvm"
EXEC_FILE_QEMU_SYSTEM_x86_64 = "qemu-system-x86_64"
EXEC_FILE_SSH = "ssh"
EXEC_FILE_VIRSH = "virsh"
EXEC_FILE_VIRT_VIEWER = "virt-viewer"
QEMU_DIR = "/var/lib/libvirt/qemu/"
# FIXME: Удалить после перевода выделения имён по шаблону из FQDN
RE_DISTRO_HOSTNAME_PATTERN = r"[^a-zA-Z0-9-]+"
RE_FQDN_PATTERN = r"^[\.a-z0-9]+$"
RE_USERNAME_PATTERN = "[a-z_][a-z0-9_-]{1,32}$"
