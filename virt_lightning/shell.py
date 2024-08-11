#!/usr/bin/env python3

import argparse
import asyncio
import curses
import grp
import logging
import os
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import libvirt
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
from virt_lightning.cli_up import CLIup
from virt_lightning.cli_viewer import CLIViewer
from virt_lightning.configuration import ProxyLegacyConfiguration as Configuration
from virt_lightning.domain_libvirt import LibvirtDomain
from virt_lightning.exceptions import (
    CannotConnectToLibvirtError,
    ImageNotFoundLocallyError,
    ImageNotFoundUpstreamError,
    VMNotRunningError,
)
from virt_lightning.network_system import NetworkSystem
from virt_lightning.storage_system import StorageSystem
from virt_lightning.tui import VirtTUI
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


def up(vmm, virt_lightning_yaml, configuration, context="default", **kwargs):
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


def ssh_config(vmm, configuration, context="default", **kwargs):
    """Generate an SSH configuration based on the running VM."""

    ssh_host_template = (
        "Host {name}\n"
        "     Hostname {ipv4}\n"
        "     User {username}\n"
        "     IdentityFile {ssh_key_file}\n"
    )

    output = ""
    groups = {}
    for domain in vmm.list_domains():
        for group in domain.groups:
            groups[group].append(domain)

        if domain.context != context:
            continue

        template = ssh_host_template

        output += template.format(
            name=domain.name,
            username=domain.username,
            ipv4=domain.ipv4.ip,
            ssh_key_file=domain.ssh_key,
        )

    for group_name, domains in groups.items():
        output += f"\n[{group_name}]"
        for domain in domains:
            output += domain.name
    return output


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
   $ vl ansible_inventory

 The file is ready to be used by Ansible:
   $ ansible all -m ping -i inventory

Commands:
    up                  Start VMs defined in virt-lightning.yaml
    down                Delete all VMs created by virt-lightning
    start               Start a new VM
    stop                Delete a VM
    images              Dump list of supported distros
    storage_dir         Dump the VM image storage directory
    ansible_inventory   Dump an inventory file for ansible
    ssh                 SSH into VM
    ssh_config          Dump an SSH config
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

    action_subparsers.add_parser(
        "storage_dir", help="Print the storage directory", parents=[parent_parser]
    )

    ssh_config_parser = action_subparsers.add_parser(
        "ssh_config",
        help="Print a ssh config of the running environment",
        parents=[parent_parser],
    )
    ssh_config_parser.add_argument("--context", **context_args)

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

    if args.action == "ansible_inventory":
        print(  # noqa: T001
            CLIAnsible.run(vmm, configuration, context="default")
        )
    elif args.action == "ssh_config":
        print(ssh_config(vmm, configuration=configuration, **vars(args)))  # noqa: T001
    elif args.action == "images":
        CLIImages.run(vmm)
    elif args.action == "storage_dir":
        logger.info(f"{vmm.storage.storage_dir}")
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
        CLIssh.run(vmm, args.name)
    elif args.action == "pull":
        CLIPull.run(vmm, configuration, args)
    elif args.action in ["up", "start"]:
        if args.action == "up":
            action_func = up
        elif args.action == "start":
            action_func = start

        try:
            action_func(vmm, configuration=configuration, **vars(args))
        except ImageNotFoundLocallyError as e:
            print(f"Image not found from url: {e.name}")  # noqa: T001
            exit(consts.ExitCode.FAIL.value)
        except CannotConnectToLibvirtError:
            how_to_fix_auth_error()
        except VMNotRunningError as e:
            print(f"The following instance is not running: {e.name}")  # noqa: T001
            exit(consts.ExitCode.FAIL.value)
    else:
        raise NotImplementedError(f"command: {args.action}")
