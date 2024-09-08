import sys
from pathlib import PosixPath
from urllib.parse import urlparse

from virt_lightning.consts import CLI_MESSAGE_USAGE, DEFAULT_VL_COMMAND
from virt_lightning.icli import ICLIcmd
from virt_lightning.image_oci_create import OCIImageAssembly


class CLIBuild(ICLIcmd):
    def __init__(self, action_subparsers, parent_parser):
        self.parser = action_subparsers.add_parser(
            "build",
            help="Build commands",
            parents=[parent_parser],
        )
        self.sub_parser = self.parser.add_subparsers(
            help="Build commands list", dest="command"
        )
        self.build_assembly_parser = self.sub_parser.add_parser(
            "assembly", help="Assembly image from prepared files"
        )
        self.build_config_parser = self.sub_parser.add_parser(
            "config", help="Build image from configuration file"
        )

    def arguments(self):
        self.build_assembly_parser.add_argument(
            "--output", help="Output path", type=str
        )
        self.build_assembly_parser.add_argument("--input", help="Input path", type=str)
        self.build_assembly_parser.add_argument("--filename", help="Filename", type=str)

        self.build_config_parser.add_argument(
            "--filename", help="Filename", type=urlparse
        )

        return self

    def context(self, args):
        return self

    @staticmethod
    def run(vmm, configuration, args):
        match args.command:
            case "assembly":
                CLIBuild.assembly(args.input, args.output, args.filename)
            case "config":
                CLIBuild.config(args.filename)
            case _:
                sys.stdout.write(CLI_MESSAGE_USAGE.format(cli=DEFAULT_VL_COMMAND))

    @staticmethod
    def assembly(src, dst, name):
        OCIImageAssembly(PosixPath(src), PosixPath(dst)).make(name)

    @staticmethod
    def config(filename):
        raise FileNotFoundError(str(filename))
