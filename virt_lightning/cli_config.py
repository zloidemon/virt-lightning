class CLIConfig:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "config", help="Dump configuration", parents=[parent_parser]
        )

    def context(self, args):
        self.parser.add_argument("--context", **args)
        return self

    @staticmethod
    def run(configuration):
        print(  # noqa: T001
            "Libvirt\n"
            f"    libvirt_uri:              {configuration.libvirt_uri}\n"
            "Network\n"
            f"    network_name:             {configuration.network_name}\n"
            f"    network_cidr:             {configuration.network_cidr}\n"
            f"    network_auto_clean_up:    {configuration.network_auto_clean_up}\n"
            "Storage\n"
            f"    storage_pool:             {configuration.storage_pool}\n"
            "User\n"
            f"    ssh_key_file:             {configuration.ssh_key_file}\n"
            f"    root_password:            {'*' * 8}\n"
        )
