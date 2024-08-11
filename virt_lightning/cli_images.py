import logging

logger = logging.getLogger("virt_lightning")


class CLIImages:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "images",
            help="List all the images available locally",
            parents=[parent_parser],
        )

    @staticmethod
    def run(vmm):
        for distro_name in vmm.storage.distro_available():
            logger.info(f"- distro: {distro_name}")
