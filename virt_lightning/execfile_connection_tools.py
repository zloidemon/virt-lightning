import virt_lightning.consts as consts
from virt_lightning.iexecfile import IExecFile


class ExecFileVirtViewer(IExecFile):
    name = consts.EXEC_FILE_VIRT_VIEWER


class ExecFileVirsh(IExecFile):
    name = consts.EXEC_FILE_VIRSH


class ExecFileSSH(IExecFile):
    name = consts.EXEC_FILE_SSH
