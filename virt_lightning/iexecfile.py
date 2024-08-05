import os
import pathlib
import shutil
import subprocess
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

    def run_cmd(self, cwd=None, *args):
        cmd = [self.entrypoint] + list(args)

        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd
        )
        outs, errs = proc.communicate()
        if proc.returncode != 0:
            raise Exception("A command has failed: ", outs, errs)
        return outs
