import curses
import sys
from virt_lightning.tui import VirtTUI
import virt_lightning.consts as consts
from virt_lightning.execfile_connection_tools import ExecFileVirtViewer


class CLIViewer:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "viewer",
            help="Open the SPICE console of a given host with virt-viewer",
            parents=[parent_parser],
        )

    def arguments(self):
        self.parser.add_argument("name", help="Name of the host", type=str, nargs="?")
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
                sys.exit(consts.ExitCode.OK.value)

        if name:
            go_viewer(vmm.get_domain_by_name(name))

        curses.wrapper(VirtTUI, sorted(vmm.list_domains()), go_viewer)
