import collections
import sys

from virt_lightning.consts import DEFAULT_VL_COMMAND


class CLIAnsible:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "ansible",
            help="Ansible commands of the running environment",
            parents=[parent_parser],
        )
        self.sub_parser = self.parser.add_subparsers(
            help="Sub commands list", dest="command"
        )
        self.inventory_parser = self.sub_parser.add_parser(
            "inventory", help="Generate inventory"
        )

    def context(self, args):
        self.parser.add_argument("--context", **args)
        return self

    @staticmethod
    def run(vmm, configuration, args):
        match args.command:
            case "inventory":
                CLIAnsible.inventory(vmm, configuration, args.context)
            case _:
                sys.stdout.write(
                    f"use {DEFAULT_VL_COMMAND} --help to see available commands\n"
                )

    @staticmethod
    def inventory(vmm, configuration, context):
        """Generate an Ansible inventory based on the running VM."""

        ssh_cmd_template = (
            "{name} ansible_host={ipv4} ansible_user={username} "
            "ansible_python_interpreter={python_interpreter} "
            'ansible_ssh_common_args="-o UserKnownHostsFile=/dev/null '
            "-o GSSAPIAuthentication=no -o GSSAPIKeyExchange=no "
            '-o StrictHostKeyChecking=no"\n'
        )

        output = ""
        groups = collections.defaultdict(list)

        for domain in vmm.list_domains():
            if domain.context != context:
                continue

            for group in domain.groups:
                groups[group].append(domain)

            template = ssh_cmd_template

            output += template.format(
                name=domain.name,
                username=domain.username,
                ipv4=domain.ipv4.ip,
                python_interpreter=domain.python_interpreter,
            )  # noqa: T001

        for group_name, domains in groups.items():
            output += f"\n[{group_name}]\n"

            for domain in domains:
                output += domain.name + "\n"

        sys.stdout.write(output)
