import logging

from virt_lightning.consts import DEFAULT_LOGGER
from virt_lightning.icli import ICLIcmd

logger = logging.getLogger(DEFAULT_LOGGER)


class CLIDown(ICLIcmd):
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "down",
            help="Destroy all the VM created with VirtLightning",
            parents=[parent_parser],
        )

    def context(self, args):
        self.parser.add_argument("--context", **args)
        return self

    def arguments(self):
        return self

    @staticmethod
    def run(vmm, configuration, context="default", **kwargs):
        """Stop and remove a running environment."""

        for domain in vmm.list_domains():
            if domain.context != context:
                continue
            logger.info("x purging %s", domain.name)
            vmm.clean_up(domain)

        if configuration.network_auto_clean_up:
            vmm.network.network_obj.destroy()
