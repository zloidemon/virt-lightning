class CLIStart:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "start", help="Start a new VM", parents=[parent_parser]
        )

    def context(self, args):
        self.parser.add_argument("--context", **args)
        return self

    def arguments(self):
        self.parser.add_argument(
            "--ssh",
            help="Automatically open a SSH connection.",
            action="store_true",
            default=False,
        )
        self.parser.add_argument("--name", help="Name of the VM", type=str)
        self.parser.add_argument("--memory", help="Memory in MB", type=int)
        self.parser.add_argument("--vcpus", help="Number of VCPUS", type=int)
        self.parser.add_argument(
            "--show-console",
            help="Suppress console output during VM creation",
            type=bool,
            dest="enable_console",
            default=True,
        )
        self.parser.add_argument("distro", help="Name of the distro", type=str)
        self.parser.add_argument(
            "--disk",
            action="extend",
            nargs=1,
            metavar="SIZE",
            help="Size of disk in GB. Multiple disks might be defined",
            type=int,
        )
        return self
