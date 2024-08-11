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
