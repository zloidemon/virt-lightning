import logging

logger = logging.getLogger("virt_lightning")


class CLIDown:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "down",
            help="Destroy all the VM created with VirtLightning",
            parents=[parent_parser],
        )

    def context(self, args):
        self.parser.add_argument("--context", **args)
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
