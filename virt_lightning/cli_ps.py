class CLIps:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "ps", help="List the VM currently running", parents=[parent_parser]
        )

    def context(self, args):
        self.parser.add_argument("--context", **args)
        return self
