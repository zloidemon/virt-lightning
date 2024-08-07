from enum import Enum, unique


@unique
class LoginMethod(Enum):
    SSH = "ssh"


@unique
class ExitCode(Enum):
    OK = 0
    FAIL = 1


DEFAULT_BASE_REGISTRY_URL = "http://localhost"
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
        "registry_urls": "",
    }
}
DEFAULT_LIBVIRT_GROUP = "libvirt"
DEFAULT_STORAGE_DIR = "/var/lib/virt-lightning/pool"
EXEC_FILE_GENISOIMAGE = "genisoimage"
EXEC_FILE_KVM = "kvm"
EXEC_FILE_MKISOFS = "mkisofs"
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
