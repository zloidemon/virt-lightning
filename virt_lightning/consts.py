from enum import Enum, unique


@unique
class LoginMethod(Enum):
    SSH = "ssh"


@unique
class ExitCode(Enum):
    OK = 0
    FAIL = 1


DEFAULT_BASE_URL = "https://virt-lightning.org"
DEFAULT_CONFIGFILE = "~/.config/virt-lightning/config.ini"
DEFAULT_USER_USERNAME = "root"
DEFAULT_USER_PASSWORD = "root"
DEFAULT_CONFIGURATION = {
    "main": {
        "libvirt_uri": "qemu:///system",
        "root_password": DEFAULT_USER_PASSWORD,
        "storage_pool": "virt-lightning",
        "network_name": "virt-lightning",
        "network_cidr": "192.168.123.0/24",
        "network_auto_clean_up": True,
        "ssh_key_file": "~/.ssh/id_rsa.pub",
        "private_hub": "",
    }
}
DEFAULT_LIBVIRT_GROUP = "libvirt"
DEFAULT_STORAGE_DIR = "/var/lib/virt-lightning/pool"
QEMU_DIR = "/var/lib/libvirt/qemu/"
KVM_BINARIES = (
    "/usr/bin/qemu-system-x86_64",
    "/usr/bin/qemu-kvm",
    "/usr/bin/kvm",
    "/usr/libexec/qemu-kvm",
)
EXEC_FILE_GENISOIMAGE = "genisoimage"
EXEC_FILE_MKISOFS = "mkisofs"
EXEC_FILE_VIRSH = "virsh"
EXEC_FILE_VIRT_VIEWER = "virt-viewer"
