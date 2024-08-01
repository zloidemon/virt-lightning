import os
import pathlib
import shutil
from abc import (
    ABCMeta,
    abstractproperty,
)


#
# Общий интерфейс для исполняемых файлов
#
class IExecFile(metaclass=ABCMeta):
    @abstractproperty
    def name(self):
        pass

    @property
    def which(self):
        exe = shutil.which(self.name)
        if exe and pathlib.PosixPath(exe).exists():
            return exe
        raise Exception(f"exec file not found: {self.name}")

    @property
    def entrypoint(self):
        return self.which

    def run(self, *args):
        os.execlp(
            str(self.entrypoint),
            str(self.entrypoint),
            *args,
        )
