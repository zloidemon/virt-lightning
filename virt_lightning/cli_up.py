class CLIup:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "up",
            help="Start the VM listed in the virt-lightning.yaml file",
            parents=[parent_parser],
        )

    def context(self, args):
        self.parser.add_argument("--context", **args)
        return self

    def arguments(self, args):
        self.add_argument("--virt-lightning-yaml", args)
        return self
