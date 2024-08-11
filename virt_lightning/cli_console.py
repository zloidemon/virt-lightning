class CLIConsole:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "console", help="Open the console of a given host", parents=[parent_parser]
        )

    def arguments(self):
        self.parser.add_argument("name", help="Name of the host", type=str, nargs="?")
        return self
