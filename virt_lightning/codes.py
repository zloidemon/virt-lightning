from enum import Enum, unique


@unique
class ExitCode(Enum):
    OK = 0
    FAIL = 1
