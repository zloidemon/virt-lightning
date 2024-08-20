import os
import sys

from virt_lightning.consts import ExitCode
from virt_lightning.execfile_connection_tools import ExecFileVirtViewer
from virt_lightning.icli import ICLIcmd
from virt_lightning.tui import menu


class CLIViewer(ICLIcmd):
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "viewer",
            help="Open the SPICE console of a given host with virt-viewer",
            parents=[parent_parser],
        )

    def arguments(self):
        self.parser.add_argument("name", help="Name of the host", type=str, nargs="?")
        return self

    def context(self, args):
        return self

    @staticmethod
    def run(vmm, configuration, name=None, **kwargs):
        def go_viewer(domain):
            pid = os.fork()
            if pid == 0:
                os.close(1)
                os.close(2)
                ExecFileVirtViewer().run(
                    "-c",
                    configuration.libvirt_uri,
                    "--domain-name",
                    domain.name,
                )
            else:
                sys.exit(ExitCode.OK.value)

        if name:
            go_viewer(vmm.get_domain_by_name(name))

        menu(vmm.list_domains(), go_viewer)
