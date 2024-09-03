#!/usr/bin/env python3

import argparse
import logging
import pathlib
import sys
import tomllib
from urllib.parse import urlparse

from virt_lightning.cli_ansible import CLIAnsible
from virt_lightning.cli_build import CLIBuild
from virt_lightning.cli_config import CLIConfig
from virt_lightning.cli_console import CLIConsole
from virt_lightning.cli_down import CLIDown
from virt_lightning.cli_help import CLIHelp
from virt_lightning.cli_images import CLIImages
from virt_lightning.cli_ps import CLIps
from virt_lightning.cli_pull import CLIPull
from virt_lightning.cli_ssh import CLIssh
from virt_lightning.cli_start import CLIStart
from virt_lightning.cli_stop import CLIStop
from virt_lightning.cli_storage import CLIStorage
from virt_lightning.cli_up import CLIup
from virt_lightning.cli_viewer import CLIViewer
from virt_lightning.configuration_legacy import ProxyLegacyConfiguration
from virt_lightning.consts import (
    CLI_MESSAGE_HELP,
    CLI_MESSAGE_USAGE,
    DEFAULT_CONFIGFILE,
    DEFAULT_LOGGER,
    DEFAULT_VL_COMMAND,
    DEFAULT_VL_CONFIGURATION_FILE,
    ExitCode,
)
from virt_lightning.network_system import NetworkSystem
from virt_lightning.storage_system import StorageSystem
from virt_lightning.vmm_builder import VMMBuilder
from virt_lightning.vmm_libvirt import VMMLibvirt

logger = logging.getLogger(DEFAULT_LOGGER)
ch = logging.StreamHandler()
logger.addHandler(ch)


class CLIBuilder:
    __context_args = {
        "default": "default",
        "help": "alternative context (default: %(default)s)",
        "dest": "context",
    }

    def __init__(self, main_parser, action_subparsers, parent_parser):
        self.main_parser = main_parser
        self.action_subparsers = action_subparsers
        self.parent_parser = parent_parser

    def add_command(self, cmd, *args, **kwargs):
        cmd(self.action_subparsers, self.parent_parser).context(
            self.__context_args
        ).arguments(*args, **kwargs)
        return self

    def build(self):
        return self.main_parser.parse_args()

    @classmethod
    def create(cls):
        main_parser = argparse.ArgumentParser()
        main_parser.add_argument(
            "--debug",
            action="store_true",
            default=False,
            help="Print extra information (default: %(default)s)",
        )
        main_parser.add_argument(
            "--config",
            help="path to configuration file",
            required=False,
            default=DEFAULT_CONFIGFILE,
            type=urlparse,
        )

        parent_parser = argparse.ArgumentParser(add_help=False)
        action_subparsers = main_parser.add_subparsers(title="action", dest="action")

        return cls(main_parser, action_subparsers, parent_parser)


#
#  FIXME: Сделать отдельный файл конфигурации и класс к нему
#
def list_from_config_file(value):
    file_path = pathlib.PosixPath(value)
    if not file_path.exists():
        raise argparse.ArgumentTypeError(f"{value} does not exist.")
    with file_path.open(encoding="UTF-8") as fd:
        content = []
        data = tomllib.loads(fd.read())
        for k, v in data.items():
            v["name"] = k
            content.append(v)
        if not isinstance(content, list):
            raise argparse.ArgumentTypeError(f"{value} should be a YAML list.")
        return content


def main():
    vl_lightning_config_args = {
        "default": DEFAULT_VL_CONFIGURATION_FILE,
        "help": f"set another {DEFAULT_VL_CONFIGURATION_FILE} file (default: %(default)s)",
        "type": list_from_config_file,
        "dest": "virt_lightning_conf",
    }
    cli_builder = CLIBuilder.create()

    cli_builder.add_command(CLIAnsible)
    cli_builder.add_command(CLIBuild)
    cli_builder.add_command(CLIConfig)
    cli_builder.add_command(CLIConsole)
    cli_builder.add_command(CLIDown)
    cli_builder.add_command(CLIImages)
    cli_builder.add_command(CLIPull)
    cli_builder.add_command(CLIStart)
    cli_builder.add_command(CLIStop)
    cli_builder.add_command(CLIStorage)
    cli_builder.add_command(CLIViewer)
    cli_builder.add_command(CLIps)
    cli_builder.add_command(CLIssh)
    cli_builder.add_command(CLIup, vl_lightning_config_args)

    args = cli_builder.build()

    if not args.action:
        usage = CLI_MESSAGE_USAGE.format(
            cli=DEFAULT_VL_COMMAND,
        )
        example = CLI_MESSAGE_HELP.format(
            cli=DEFAULT_VL_COMMAND,
            conf=DEFAULT_VL_CONFIGURATION_FILE,
        )
        sys.stdout.write(f"{usage}\n")
        sys.stdout.write(f"{example}\n")
        exit(ExitCode.FAIL.value)

    configuration = ProxyLegacyConfiguration.load(args.config)
    vmm_builder = VMMBuilder(configuration)

    vmm_builder.set_storage(StorageSystem)
    vmm_builder.set_network(NetworkSystem)
    vmm_builder.set_vmm(VMMLibvirt)

    vmm = vmm_builder.connect()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    match args.action:
        case "ansible":
            CLIAnsible.run(vmm, configuration, args)
        case "images":
            CLIImages.run(vmm)
        case "storage":
            CLIStorage.run(vmm.storage, args)
        case "down" | "stop":
            CLIDown.run(vmm, configuration=configuration, **vars(args))
        case "ps":
            CLIps.run(vmm, configuration=configuration)
        case "build":
            CLIBuild.run(vmm, configuration, args)
        case "config":
            CLIConfig.run(configuration)
        case "console":
            CLIConsole.run(vmm, configuration=configuration, name=args.name)
        case "viewer":
            CLIViewer.run(vmm, configuration=configuration, name=args.name)
        case "ssh":
            CLIssh.run(vmm, configuration, args)
        case "pull":
            CLIPull.run(vmm, configuration, args)
        case "start":
            CLIStart.run(vmm, configuration=configuration, **vars(args))
        case "up":
            CLIup.run(vmm, args.virt_lightning_conf, configuration=configuration)
        case _:
            CLIHelp.run()
            raise NotImplementedError(f"command: {args.action}")
