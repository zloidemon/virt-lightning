#!/usr/bin/env python3

import argparse
import grp
import logging
import os
import pathlib
from urllib.parse import urlparse

import yaml

import virt_lightning.consts as consts
from virt_lightning.cli_ansible import CLIAnsible
from virt_lightning.cli_config import CLIConfig
from virt_lightning.cli_console import CLIConsole
from virt_lightning.cli_down import CLIDown
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


def get_local_libvirt_group():
    for entry in grp.getgrall():
        if entry.gr_name == consts.DEFAULT_LIBVIRT_GROUP:
            return (entry.gr_name, entry.gr_gid)


def how_to_fix_auth_error():
    import getpass

    libvirt_group = get_local_libvirt_group()
    if not libvirt_group:
        return
    group, gid = libvirt_group
    if gid not in os.getgroups():
        print("Virt-Lightning cannot access the local libvirt service.")  # noqa: T001
        print(  # noqa: T001
            f"Your user should probably be in the {group} group. "
            f"You can add the user {getpass. getuser()} in the group {group} with the "
            "following command:"
        )
        print(  # noqa: T001
            f"    sudo usermod --append --groups libvirt {getpass.getuser()}"
        )


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
    title = "Virt-Lightning"

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

    CLIDown(action_subparsers, parent_parser).context(context_args)
    CLIStart(action_subparsers, parent_parser).context(context_args).arguments()
    CLIssh(action_subparsers, parent_parser).arguments()
    CLIViewer(action_subparsers, parent_parser).arguments()
    CLIConsole(action_subparsers, parent_parser).arguments()
    CLIStop(action_subparsers, parent_parser).arguments()
    CLIPull(action_subparsers, parent_parser).arguments()
    CLIAnsible(action_subparsers, parent_parser).context(context_args)
    CLIConfig(action_subparsers, parent_parser).context(context_args)
    CLIps(action_subparsers, parent_parser).context(context_args)
    CLIup(action_subparsers, parent_parser).context(context_args).arguments(
        vl_lightning_yaml_args
    )
    CLIImages(action_subparsers, parent_parser)
    CLIStorage(action_subparsers, parent_parser).arguments()

    args = main_parser.parse_args()
    if not args.action:
        print(title)  # noqa: T001
        print(usage)  # noqa: T001
        print(example)  # noqa: T001
        exit(consts.ExitCode.FAIL.value)

    configuration = Configuration(args.config)
    builder = VMMBuilder(configuration)

    builder.set_storage(StorageSystem)
    builder.set_network(NetworkSystem)
    builder.set_vmm(VMMLibvirt)

    vmm = builder.connect()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.action == "ansible":
        CLIAnsible.run(vmm, configuration, args)
    elif args.action == "images":
        CLIImages.run(vmm)
    elif args.action == "storage":
        CLIStorage.run(vmm.storage, args)
    elif args.action == "down" or args.action == "stop":
        CLIDown.run(vmm, configuration=configuration, **vars(args))
    elif args.action == "ps":
        CLIps.run(vmm, configuration=configuration)
    elif args.action == "config":
        CLIConfig.run(configuration)
    elif args.action == "console":
        CLIConsole.run(vmm, configuration=configuration, name=args.name)
    elif args.action == "viewer":
        CLIViewer.run(vmm, configuration=configuration, name=args.name)
    elif args.action == "ssh":
        CLIssh.run(vmm, configuration, args)
    elif args.action == "pull":
        CLIPull.run(vmm, configuration, args)
    elif args.action == "start":
        CLIStart.run(vmm, configuration=configuration, **vars(args))
    elif args.action == "up":
        CLIup.run(vmm, args.virt_lightning_yaml, configuration=configuration)
    else:
        how_to_fix_auth_error()
        raise NotImplementedError(f"command: {args.action}")
