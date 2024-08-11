from virt_lightning.downloader_native import DownloaderNative
from virt_lightning.exceptions import ImageNotFoundUpstreamError
import virt_lightning.consts as consts


class CLIPull:
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "pull", help="Pull a VM image", parents=[parent_parser]
        )

    def arguments(self):
        self.parser.add_argument("distro", help="Name of the VM image", type=str)
        return self

    @staticmethod
    def run(vmm, configuration, args):
        try:
            downloader = DownloaderNative(
                configuration,
                vmm.storage.storage_dir,
            )
            downloader.pull(**vars(args))
        except ImageNotFoundUpstreamError:
            print(  # noqa: T001
                f"Distro {args.distro} cannot be downloaded.\n"
                f"  Visit {consts.BASE_URL}/images/ or private image hub"
                "to get an up to date list."
            )
            exit(consts.ExitCode.FAIL.value)
