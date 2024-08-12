#!/usr/bin/env python3

import argparse
import logging
import pathlib
import sys
from urllib.parse import urlparse

import yaml

import virt_lightning.consts as consts
from virt_lightning.cli_ansible import CLIAnsible
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
from virt_lightning.configuration import ProxyLegacyConfiguration as Configuration
from virt_lightning.network_system import NetworkSystem
from virt_lightning.storage_system import StorageSystem
from virt_lightning.vmm_builder import VMMBuilder
from virt_lightning.vmm_libvirt import VMMLibvirt

logger = logging.getLogger("virt_lightning")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
logger.addHandler(ch)


class CLIBuilder:
    def __init__(self, action_subparsers, parent_parser, context_args):
        self.action_subparsers = action_subparsers
        self.parent_parser = parent_parser
        self.context_args = context_args

    def add_command(self, cmd, *args, **kwargs):
        cmd(self.action_subparsers, self.parent_parser).context(
            self.context_args
        ).arguments(*args, **kwargs)
        return self


def list_from_yaml_file(value):
    file_path = pathlib.PosixPath(value)
    if not file_path.exists():
        raise argparse.ArgumentTypeError(f"{value} does not exist.")
    with file_path.open(encoding="UTF-8") as fd:
        content = yaml.safe_load(fd.read())
        if not isinstance(content, list):
            raise argparse.ArgumentTypeError(f"{value} should be a YAML list.")
        return content


def main():
    usage = """
usage: vl [--debug DEBUG] [--config CONFIG] COMMAND

Run vl without a command to see list of accepted commands.
"""
    example = """
Example:

 We export the list of the distro in the virt-lightning.yaml file.
   $ vl images > virt-lightning.yaml

 For each line of the virt-lightning.yaml, start a VM with the associated distro.
   $ vl up

 Once the VM are up, we can generate an Ansible inventory file:
   $ vl ansible inventory

 The file is ready to be used by Ansible:
   $ ansible all -m ping -i inventory

Commands:
    up                  Start VMs defined in virt-lightning.yaml
    down                Delete all VMs created by virt-lightning
    start               Start a new VM
    stop                Delete a VM
    images              Dump list of supported distros
    storage             Dump the VM image storage directory
    ansible             Ansible commands
    ssh                 SSH into VM
    console             Open console on a VM
    viewer              Open VM with virt-viewer
    ps                  Get list of running VM's
    config              Dump configuration
    """

    vl_lightning_yaml_args = {
        "default": "virt-lightning.yaml",
        "help": "point on an alternative virt-lightning.yaml file (default: %(default)s)",
        "type": list_from_yaml_file,
        "dest": "virt_lightning_yaml",
    }
    context_args = {
        "default": "default",
        "help": "alternative context (default: %(default)s)",
        "dest": "context",
    }

    parent_parser = argparse.ArgumentParser(add_help=False)
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
        default=consts.DEFAULT_CONFIGFILE,
        type=urlparse,
    )

    action_subparsers = main_parser.add_subparsers(title="action", dest="action")

    cli_builder = CLIBuilder(action_subparsers, parent_parser, context_args)
    cli_builder.add_command(CLIAnsible)
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
    cli_builder.add_command(CLIup, vl_lightning_yaml_args)

    args = main_parser.parse_args()

    if not args.action:
        sys.stdout.write(f"{usage}\n")
        sys.stdout.write(f"{example}\n")
        exit(consts.ExitCode.FAIL.value)

    configuration = Configuration(args.config)
    builder = VMMBuilder(configuration)

    builder.set_storage(StorageSystem)
    builder.set_network(NetworkSystem)
    builder.set_vmm(VMMLibvirt)

    vmm = builder.connect()

    if args.debug:
        logger.setLevel(logging.DEBUG)

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
            CLIup.run(vmm, args.virt_lightning_yaml, configuration=configuration)
        case _:
            CLIHelp.run()
            raise NotImplementedError(f"command: {args.action}")
