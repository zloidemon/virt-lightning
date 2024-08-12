import sys

from virt_lightning.icli import ICLIcmd

_CONFIGURATION_MESSAGE = """
Libvirt
    libvirt_uri:              {configuration.libvirt_uri}
Network
    network_name:             {configuration.network_name}
    network_cidr:             {configuration.network_cidr}
    network_auto_clean_up:    {configuration.network_auto_clean_up}
Storage
    storage_pool:             {configuration.storage_pool}
User
    ssh_key_file:             {configuration.ssh_key_file}
    root_password:            {root_password}
"""


class CLIConfig(ICLIcmd):
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "config", help="Dump configuration", parents=[parent_parser]
        )

    def arguments(self):
        return self

    def context(self, args):
        self.parser.add_argument("--context", **args)
        return self

    @staticmethod
    def run(configuration):
        msg = _CONFIGURATION_MESSAGE.format(
            configuration=configuration,
            root_password='*' * 8,
        )
        sys.stdout.write(f"{msg}\n")
