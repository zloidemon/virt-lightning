import logging

logger = logging.getLogger("virt_lightning")


class CLIStorage:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "storage", help="Print the storage directory", parents=[parent_parser]
        )

    def arguments(self):
        self.parser.add_argument(
            "--dir",
            help="Storage dir",
            type=bool,
            dest="enable_console",
            default=True,
        )
        return self

    @staticmethod
    def run(storage, args):
        logger.info(f"{storage.storage_dir}")
