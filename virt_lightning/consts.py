from enum import Enum, unique
from pathlib import PosixPath


@unique
class LoginMethod(Enum):
    SSH = "ssh"


DEFAULT_BASE_URL = "https://virt-lightning.org"
DEFAULT_CONFIGFILE = PosixPath("~/.config/virt-lightning/config.ini")
