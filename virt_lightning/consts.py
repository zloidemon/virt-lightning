from enum import Enum, unique
from pathlib import PosixPath


@unique
class LoginMethod(Enum):
    SSH = 'ssh'

DEFAULT_CONFIGFILE = PosixPath("~/.config/virt-lightning/config.ini")
