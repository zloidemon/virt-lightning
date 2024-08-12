import asyncio
import logging
import sys

import libvirt

from virt_lightning.domain_libvirt import LibvirtDomain
from virt_lightning.icli import ICLIcmd

logger = logging.getLogger("virt_lightning")


class CLIStart(ICLIcmd):
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "start", help="Start a new VM", parents=[parent_parser]
        )

    def context(self, args):
        self.parser.add_argument("--context", **args)
        return self

    def arguments(self):
        self.parser.add_argument(
            "--ssh",
            help="Automatically open a SSH connection.",
            action="store_true",
            default=False,
        )
        self.parser.add_argument("--name", help="Name of the VM", type=str)
        self.parser.add_argument("--memory", help="Memory in MB", type=int)
        self.parser.add_argument("--vcpus", help="Number of VCPUS", type=int)
        self.parser.add_argument(
            "--show-console",
            help="Suppress console output during VM creation",
            type=bool,
            dest="enable_console",
            default=True,
        )
        self.parser.add_argument("distro", help="Name of the distro", type=str)
        self.parser.add_argument(
            "--disk",
            action="extend",
            nargs=1,
            metavar="SIZE",
            help="Size of disk in GB. Multiple disks might be defined",
            type=int,
        )
        return self

    @staticmethod
    def run(
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
