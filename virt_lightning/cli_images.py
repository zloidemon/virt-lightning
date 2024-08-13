import logging

from virt_lightning.consts import DEFAULT_LOGGER
from virt_lightning.icli import ICLIcmd

logger = logging.getLogger(DEFAULT_LOGGER)


class CLIImages(ICLIcmd):
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "images",
            help="List all the images available locally",
            parents=[parent_parser],
        )

    def arguments(self):
        return self

    def context(self, args):
        return self

    @staticmethod
    def run(vmm):
        for distro_name in vmm.storage.distro_available():
            logger.info(f"- distro: {distro_name}")
