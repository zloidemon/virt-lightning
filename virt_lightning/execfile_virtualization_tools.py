from virt_lightning.consts import (
    EXEC_FILE_KVM,
    EXEC_FILE_QEMU_IMG,
    EXEC_FILE_QEMU_KVM,
    EXEC_FILE_QEMU_SYSTEM_x86_64,
)
from virt_lightning.iexecfile import IExecFile


class ExecFileVirtTool(IExecFile):
    def __init__(self):
        self.__name = None
        self.__binaries = (
            EXEC_FILE_KVM,
            EXEC_FILE_QEMU_KVM,
            EXEC_FILE_QEMU_SYSTEM_x86_64,
        )

    @property
    def name(self):
        return self.__name

    @property
    def entrypoint(self):
        for binary in self.__binaries:
            self.__name = binary
            try:
                return self.which
            except Exception:  # noqa: B902
                continue

        raise Exception("Failed to find the kvm binary")


class ExecFileQemuIMG(IExecFile):
    name = EXEC_FILE_QEMU_IMG
