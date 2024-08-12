import logging

from virt_lightning.exceptions import VMNotFoundError
from virt_lightning.icli import ICLIcmd

logger = logging.getLogger("virt_lightning")


class CLIStop(ICLIcmd):
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "stop", help="Stop and delete a VM", parents=[parent_parser]
        )

    def arguments(self):
        self.parser.add_argument("name", help="Name of the VM", type=str)
        return self

    def context(self, args):
        return self

    @staticmethod
    def run(vmm, configuration, **kwargs):
        """Stop and delete a given VM."""
        domain = vmm.get_domain_by_name(kwargs["name"])
        if not domain:
            vm_list = [d.name for d in vmm.list_domains()]
            if vm_list:
                logger.info(
                    "No VM called %s in: %s", kwargs.get("name"), ", ".join(vm_list)
                )
            else:
                logger.info("No running VM.")
            raise VMNotFoundError(kwargs["name"])
        vmm.clean_up(domain)
