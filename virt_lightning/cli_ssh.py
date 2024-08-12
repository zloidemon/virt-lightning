import curses
import sys

from virt_lightning.consts import DEFAULT_VL_COMMAND
from virt_lightning.exceptions import VMNotFoundError
from virt_lightning.execfile_connection_tools import ExecFileSSH
from virt_lightning.tui import VirtTUI


class CLIssh:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "ssh", help="SSH commands", parents=[parent_parser]
        )
        self.sub_parser = self.parser.add_subparsers(
            help="Sub commands list", dest="command"
        )
        self.connect_parser = self.sub_parser.add_parser(
            "connect", help="SSH to a given host"
        )
        self.config_parser = self.sub_parser.add_parser(
            "config", help="Print a ssh config of the running environment"
        )

    def arguments(self):
        self.connect_parser.add_argument(
            "name", help="Name of the host", type=str, nargs="?"
        )
        return self

    @staticmethod
    def run(vmm, configuration, args):
        match args.command:
            case "connect":
                CLIssh.connect(vmm, configuration, args.name)
            case "config":
                CLIssh.config(vmm, configuration, context="default")
            case _:
                sys.stdout.write(
                    f"use {DEFAULT_VL_COMMAND} --help to see available commands\n"
                )

    @staticmethod
    def config(vmm, configuration, context="default"):
        """Generate an SSH configuration based on the running VM."""

        ssh_host_template = (
            "Host {name}\n"
            "     Hostname {ipv4}\n"
            "     User {username}\n"
            "     IdentityFile {ssh_key_file}\n"
        )

        output = ""
        groups = {}
        for domain in vmm.list_domains():
            for group in domain.groups:
                groups[group].append(domain)

            if domain.context != context:
                continue

            template = ssh_host_template

            output += template.format(
                name=domain.name,
                username=domain.username,
                ipv4=domain.ipv4.ip,
                ssh_key_file=domain.ssh_key,
            )

        for group_name, domains in groups.items():
            output += f"\n[{group_name}]"
            for domain in domains:
                output += domain.name

        sys.stdout.write(output)

    @staticmethod
    def connect(vmm, configuration, name):
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
