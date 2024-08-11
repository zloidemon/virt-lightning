import curses
from virt_lightning.tui import VirtTUI
from virt_lightning.exceptions import VMNotFoundError
from virt_lightning.execfile_connection_tools import ExecFileSSH


class CLIssh:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "ssh", help="SSH to a given host", parents=[parent_parser]
        )

    def arguments(self):
        self.parser.add_argument("name", help="Name of the host", type=str, nargs="?")
        return self

    @staticmethod
    def run(vmm, name):
        def go_ssh(domain):
            ExecFileSSH().run(
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "UserKnownHostsFile=/dev/null",
                f"{domain.username}@{domain.ipv4.ip}",
            )

        if name:
            domain = vmm.get_domain_by_name(name)
            if not domain:
                raise VMNotFoundError(name)
            go_ssh(domain)

        curses.wrapper(
            VirtTUI,
            sorted(vmm.list_domains()),
            go_ssh,
        )
