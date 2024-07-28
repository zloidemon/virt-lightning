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
