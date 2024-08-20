from virt_lightning.execfile_connection_tools import ExecFileVirsh
from virt_lightning.icli import ICLIcmd
from virt_lightning.tui import menu


class CLIConsole(ICLIcmd):
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "console", help="Open the console of a given host", parents=[parent_parser]
        )

    def arguments(self):
        self.parser.add_argument("name", help="Name of the host", type=str, nargs="?")
        return self

    def context(self, args):
        return self

    @staticmethod
    def run(vmm, configuration, name=None, **kwargs):
        def go_console(domain):
            ExecFileVirsh().run(
                "-c",
                configuration.libvirt_uri,
                "console",
                domain.name,
            )

        if name:
            go_console(vmm.get_domain_by_name(name))

        menu(vmm.list_domains(), go_console)
