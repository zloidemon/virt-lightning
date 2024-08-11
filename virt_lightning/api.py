#!/usr/bin/env python3

import asyncio
import logging
import sys
from concurrent.futures import ThreadPoolExecutor

import libvirt

from virt_lightning.domain_libvirt import LibvirtDomain

logger = logging.getLogger("virt_lightning")


def up(vmm, virt_lightning_yaml, configuration, context="default", **kwargs):
    """Create a list of VM."""

    def _lifecycle_callback(conn, dom, state, reason, opaque):  # noqa: N802
        if state == 1:
            logger.info("+ %s QEMU agent found", dom.name())

    loop = asyncio.get_event_loop()

    for hosts in virt_lightning_yaml:
        vmm.storage.ensure_image_exists(configuration, hosts["distro"])

    #
    # FIXME: Перенести константы в конфигурацию
    #
    vmm.conn.setKeepAlive(interval=5, count=3)
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


def start(
    vmm,
    configuration,
    context="default",
    enable_console=False,
    console_fd=None,
    **kwargs,
):
    """Start a single VM."""
    host = {
        k: kwargs[k] for k in ["name", "distro", "memory", "vcpus"] if kwargs.get(k)
    }
    if kwargs.get("disk"):
        host.update({"disks": [{"size": x} for x in kwargs["disk"]]})

    vmm.storage.ensure_image_exists(configuration, host["distro"])
    domain = LibvirtDomain._start_domain(vmm, host, context, configuration)

    if not domain:
        return None

    loop = asyncio.get_event_loop()

    if enable_console:
        import time

        if console_fd is None:
            console_fd = sys.stdout

        time.sleep(4)
        stream = vmm.conn.newStream(libvirt.VIR_STREAM_NONBLOCK)
        console = domain.dom.openConsole(None, stream, 0)

        def stream_callback(stream, events, _):
            content = stream.recv(1024 * 1024).decode("utf-8", errors="ignore")
            console_fd.write(content)

        stream.eventAddCallback(
            libvirt.VIR_STREAM_EVENT_READABLE, stream_callback, console
        )

    async def deploy():
        await domain.reachable()

    loop.run_until_complete(deploy())
    logger.info(  # noqa: T001
        (
            "\033[0m\n**** System is online ****\n"
            "To connect use:\n"
            "  vl console %s (virsh console)"
            "  vl ssh %s"
        ),
        domain.name,
        domain.name,
    )
    return domain
