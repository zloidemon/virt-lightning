class CLIPull:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "pull", help="Pull a VM image", parents=[parent_parser]
        )

    def arguments(self):
        self.parser.add_argument("distro", help="Name of the VM image", type=str)
        return self
