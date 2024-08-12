import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

import libvirt

from virt_lightning.domain_libvirt import LibvirtDomain
from virt_lightning.icli import ICLIcmd

logger = logging.getLogger("virt_lightning")


class CLIup(ICLIcmd):
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "up",
            help="Start the VM listed in the virt-lightning.yaml file",
            parents=[parent_parser],
        )

    def arguments(self, args):
        self.parser.add_argument("--virt-lightning-yaml", **args)
        return self

    def context(self, args):
        self.parser.add_argument("--context", **args)
        return self

    @staticmethod
    def run(vmm, virt_lightning_yaml, configuration, context="default"):
        """Create a list of VM."""

        def _lifecycle_callback(conn, dom, state, reason, opaque):  # noqa: N802
            if state == 1:
                logger.info("+ %s QEMU agent found", dom.name())

        loop = asyncio.get_event_loop()

        for hosts in virt_lightning_yaml:
            vmm.storage.ensure_image_exists(configuration, hosts["distro"])

        vmm.conn.domainEventRegisterAny(
            None,
            libvirt.VIR_DOMAIN_EVENT_ID_AGENT_LIFECYCLE,
            _lifecycle_callback,
            None,
        )

        async def deploy():
            futures = []
            for host in virt_lightning_yaml:
                futures.append(
                    loop.run_in_executor(
                        ThreadPoolExecutor(max_workers=10),
                        LibvirtDomain._start_domain,
                        vmm,
                        host,
                        context,
                        configuration,
                    )
                )

            domain_reachable_futures = []
            for f in futures:
                await f
                domain = f.result()
                if domain:
                    domain_reachable_futures.append(domain.reachable())
            logger.info("waiting...")

            await asyncio.gather(*domain_reachable_futures)

        loop.run_until_complete(deploy())
        logger.info("+ You are all set")
