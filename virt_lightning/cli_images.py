class CLIImages:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "images",
            help="List all the images available locally",
            parents=[parent_parser],
        )
