class CLIAnsible:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "ansible_inventory",
            help="Print an ansible_inventory of the running environment",
            parents=[parent_parser],
        )

    def context(self, args):
        self.parser.add_argument("--context", **args)
        return self
