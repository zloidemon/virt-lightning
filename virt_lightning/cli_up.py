import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

import libvirt

from virt_lightning.consts import DEFAULT_LOGGER, DEFAULT_VL_CONFIGURATION_FILE
from virt_lightning.domain_libvirt import LibvirtDomain
from virt_lightning.icli import ICLIcmd

logger = logging.getLogger(DEFAULT_LOGGER)


class CLIup(ICLIcmd):
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "up",
            help=f"Run from {DEFAULT_VL_CONFIGURATION_FILE} file",
            parents=[parent_parser],
        )

    def arguments(self, args):
        self.parser.add_argument("--virt-lightning-conf", **args)
        return self

    def context(self, args):
        self.parser.add_argument("--context", **args)
        return self

    @staticmethod
    def run(vmm, virt_lightning_conf, configuration, context="default"):
        """Create a list of VM."""

        def _lifecycle_callback(conn, dom, state, reason, opaque):  # noqa: N802
            if state == 1:
                logger.info("+ %s QEMU agent found", dom.name())

        loop = asyncio.get_event_loop()

        for hosts in virt_lightning_conf:
            vmm.storage.ensure_image_exists(configuration, hosts["distro"])

        vmm.conn.domainEventRegisterAny(
            None,
            libvirt.VIR_DOMAIN_EVENT_ID_AGENT_LIFECYCLE,
            _lifecycle_callback,
            None,
        )

        async def deploy():
            futures = []
            for host in virt_lightning_conf:
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
