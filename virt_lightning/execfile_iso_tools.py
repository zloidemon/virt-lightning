from virt_lightning.consts import (
    EXEC_FILE_GENISOIMAGE,
    EXEC_FILE_MKISOFS,
)
from virt_lightning.iexecfile import IExecFile


class ExecFileISOTool(IExecFile):
    def __init__(self):
        self.__name = None
        self.__binaries = (EXEC_FILE_GENISOIMAGE, EXEC_FILE_MKISOFS)

    @property
    def name(self):
        return self.__name

    @property
    def entrypoint(self):
        for binary in self.__binaries:
            self.__name = binary
            if not self.which:
                continue
            else:
                return self.which

        error_msg = (
            f"Failed to find in PATH: {','.join(self.__binaries)}"
            "\nPlease install genisoimage tool"
        )
        raise Exception(error_msg)
