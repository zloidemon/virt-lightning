import logging
import sys
from importlib.metadata import version as get_version

from virt_lightning.consts import DEFAULT_LOGGER
from virt_lightning.icli import ICLIcmd

logger = logging.getLogger(DEFAULT_LOGGER)


class CLIVersion(ICLIcmd):
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "version",
            help="Show version",
            parents=[parent_parser],
        )

    def arguments(self):
        return self

    def context(self, args):
        return self

    @staticmethod
    def run():
        package_version = get_version("virt-lightning")
        sys.stdout.write(f"{package_version}\n")
