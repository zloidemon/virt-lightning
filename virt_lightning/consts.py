from enum import Enum, unique
from pathlib import PosixPath


@unique
class LoginMethod(Enum):
    SSH = "ssh"


@unique
class ExitCode(Enum):
    OK = 0
    FAIL = 1


DEFAULT_BASE_URL = "https://virt-lightning.org"
DEFAULT_CONFIGFILE = PosixPath("~/.config/virt-lightning/config.ini")
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
