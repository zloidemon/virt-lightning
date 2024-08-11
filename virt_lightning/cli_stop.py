class CLIStop:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "stop", help="Stop and delete a VM", parents=[parent_parser]
        )

    def arguments(self):
        self.parser.add_argument("name", help="Name of the VM", type=str)
        return self
