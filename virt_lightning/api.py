#!/usr/bin/env python3

import asyncio
import collections
import ipaddress
import logging
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

import libvirt

import virt_lightning.consts as consts
import virt_lightning.vmm_libvirt as vl
from virt_lightning.disk_system import DiskSystem
from virt_lightning.exceptions import (
    CannotConnectToLibvirtError,
    VMNotFoundError,
    VMNotRunningError,
)

logger = logging.getLogger("virt_lightning")


def libvirt_callback(userdata, err):
    pass


libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)


def _register_aio_virt_impl(loop):
    # Ensure we may call shell.up() multiple times
    # from the same asyncio program.
    loop = loop or asyncio.get_event_loop()
    if loop not in _register_aio_virt_impl.aio_virt_bindinds:
        try:
            import libvirtaio

            libvirtaio.virEventRegisterAsyncIOImpl(loop=loop)
        except ImportError:
            libvirt.virEventRegisterDefaultImpl()
        _register_aio_virt_impl.aio_virt_bindinds[loop] = True


_register_aio_virt_impl.__dict__["aio_virt_bindinds"] = {}


def _connect_libvirt(uri):
    try:
        if urlparse(uri).netloc == "":
            return libvirt.open(uri)
        else:
            raise NotImplementedError("Only local access allowed")
    except libvirt.libvirtError as e:
        if e.get_error_code() == libvirt.VIR_ERR_AUTH_UNAVAILABLE:
            raise CannotConnectToLibvirtError() from None
        raise


def _start_domain(hv, host, context, configuration):
    #
    # FIXME: Убрать replace() у названии образа. Надо хранить по иному для
    #        новой схемы хранения образов.
    #
    distro = host["distro"].replace(":", "-")
    #
    # FIXME: Переделать выделение имен на использование FQDN
    #
    if "name" not in host:
        host["name"] = re.sub(consts.RE_DISTRO_HOSTNAME_PATTERN, "", distro)

    domain = hv.get_domain_by_name(host["name"])
    if not domain:
        pass
    elif domain.dom.isActive():
        logger.info(f"Skipping {host['name']}, already here.")
        return
    else:
        logger.info(f"Skipping {host['name']}, already here but is not running.")
        logger.info(
            f"You can restart it with: virsh -c {configuration.libvirt_uri} start {host['name']}"
        )
        logger.info(f"You can also destroy the instance with: vl stop {host['name']}")
        raise VMNotRunningError(host["name"])

    logger.info(f"^ {host['name']} ")

    user_config = {
        "groups": host.get("groups"),
        "memory": host.get("memory"),
        "python_interpreter": host.get("python_interpreter"),
        "root_password": host.get("root_password", configuration.root_password),
        "ssh_key_file": host.get("ssh_key_file", configuration.ssh_key_file),
        "username": host.get("username"),
        "vcpus": host.get("vcpus"),
        "fqdn": host.get("fqdn"),
        "default_nic_mode": host.get("default_nic_model"),
        "bootcmd": host.get("bootcmd"),
        "runcmd": host.get("runcmd"),
        "meta_data_media_type": host.get("meta_data_media_type"),
        "default_bus_type": host.get("default_bus_type"),
    }
    domain = hv.create_domain(name=host["name"], distro=distro)
    hv.configure_domain(domain, user_config)
    domain.context = context
    networks = host.get("networks", [{}])
    for i, network in enumerate(networks):
        if "network" not in network:
            network["network"] = configuration.network_name
        if i == 0 and not network.get("ipv4"):
            network["ipv4"] = hv.network.get_free_ipv4(hv.list_domains())
        ipv4 = network.get("ipv4")
        if ipv4:
            network["mac"] = hv.network.reuse_mac_address(
                network["network"], host["name"], ipaddress.ip_interface(ipv4)
            )
        domain.attach_network(**network)

    if "root_disk_size" in host:
        logger.debug("The key 'root_disk_size' is deprecated. Use 'disks' instead")

    disks = host.get("disks", [{"size": 15}])
    for i, disk in enumerate(disks):
        size = 1
        if "size" in disk:
            size = int(disk["size"])

        # Old behavior
        if "disks" not in host and "root_disk_size" in host:
            size = int(host["root_disk_size"])

        volume = DiskSystem(None, hv.storage, hv.network).create(
            name=f"{host['name']}-{i}", backing_on=(distro if i == 0 else ""), size=size
        )
        domain.attach_disk(volume=volume)

    hv.start(domain, metadata_format=host.get("metadata_format", {}))
    return domain


def up(virt_lightning_yaml, configuration, context="default", **kwargs):
    """Create a list of VM."""

    def _lifecycle_callback(conn, dom, state, reason, opaque):  # noqa: N802
        if state == 1:
            logger.info("+ %s QEMU agent found", dom.name())

    loop = kwargs.get("loop") or asyncio.get_event_loop()
    _register_aio_virt_impl(loop)

    conn = _connect_libvirt(configuration.libvirt_uri)
    hv = vl.VMMLibvirt(conn)

    hv.network.init_network(configuration.network_name, configuration.network_cidr)
    hv.storage.init_storage_pool(configuration.storage_pool)

    for hosts in virt_lightning_yaml:
        hv.storage.ensure_image_exists(configuration, hosts["distro"])

    conn = _connect_libvirt(configuration.libvirt_uri)
    #
    # FIXME: Перенести константы в конфигурацию
    #
    conn.setKeepAlive(interval=5, count=3)
    conn.domainEventRegisterAny(
        None,
        libvirt.VIR_DOMAIN_EVENT_ID_AGENT_LIFECYCLE,
        _lifecycle_callback,
        None,
    )

    pool = ThreadPoolExecutor(max_workers=10)

    async def deploy():
        futures = []
        for host in virt_lightning_yaml:
            futures.append(
                loop.run_in_executor(
                    pool, _start_domain, hv, host, context, configuration
                )
            )

        domain_reachable_futures = []
        for f in futures:
            await f
            domain = f.result()
            if domain:
                domain_reachable_futures.append(domain.reachable())
        logger.info("... ok Waiting...")

        await asyncio.gather(*domain_reachable_futures)

    loop.run_until_complete(deploy())
    logger.info("+ You are all set")


def start(
    configuration, context="default", enable_console=False, console_fd=None, **kwargs
):
    """Start a single VM."""
    conn = _connect_libvirt(configuration.libvirt_uri)
    hv = vl.VMMLibvirt(conn)
    hv.network.init_network(configuration.network_name, configuration.network_cidr)
    hv.storage.init_storage_pool(configuration.storage_pool)
    host = {
        k: kwargs[k] for k in ["name", "distro", "memory", "vcpus"] if kwargs.get(k)
    }
    if kwargs.get("disk"):
        host.update({"disks": [{"size": x} for x in kwargs["disk"]]})
    hv.storage.ensure_image_exists(configuration, host["distro"])
    domain = _start_domain(hv, host, context, configuration)
    if not domain:
        return

    loop = kwargs.get("loop") or asyncio.get_event_loop()

    if enable_console:
        import time

        if console_fd is None:
            console_fd = sys.stdout

        time.sleep(4)
        stream = conn.newStream(libvirt.VIR_STREAM_NONBLOCK)
        console = domain.dom.openConsole(None, stream, 0)

        _register_aio_virt_impl(loop=kwargs.get("loop"))

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


def stop(vmm, configuration, **kwargs):
    """Stop and delete a given VM."""
    domain = vmm.get_domain_by_name(kwargs["name"])
    if not domain:
        vm_list = [d.name for d in vmm.list_domains()]
        if vm_list:
            logger.info(
                "No VM called %s in: %s", kwargs.get("name"), ", ".join(vm_list)
            )
        else:
            logger.info("No running VM.")
        raise VMNotFoundError(kwargs["name"])
    vmm.clean_up(domain)


def ansible_inventory(vmm, configuration, context="default", **kwargs):
    """Generate an Ansible inventory based on the running VM."""

    ssh_cmd_template = (
        "{name} ansible_host={ipv4} ansible_user={username} "
        "ansible_python_interpreter={python_interpreter} "
        'ansible_ssh_common_args="-o UserKnownHostsFile=/dev/null '
        "-o GSSAPIAuthentication=no -o GSSAPIKeyExchange=no "
        '-o StrictHostKeyChecking=no"\n'
    )

    output = ""
    groups = collections.defaultdict(list)
    for domain in vmm.list_domains():
        if domain.context != context:
            continue

        for group in domain.groups:
            groups[group].append(domain)

        template = ssh_cmd_template

        output += template.format(
            name=domain.name,
            username=domain.username,
            ipv4=domain.ipv4.ip,
            python_interpreter=domain.python_interpreter,
        )  # noqa: T001

    for group_name, domains in groups.items():
        output += f"\n[{group_name}]\n"
        for domain in domains:
            output += domain.name + "\n"
    return output


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


def ps(vmm, configuration, context="default", name=None, **kwargs):
    """Returns the status of the VM of the envionment."""

    for domain in vmm.list_domains():
        if context and context != domain.context:
            continue
        name = domain.name
        if not domain.ipv4:  # Not a VL managed VM
            continue
        yield {
            "name": name,
            "ipv4": domain.ipv4 and str(domain.ipv4.ip),
            "context": domain.context,
            "username": domain.username,
            "distro": domain.distro,
        }


def exec_ssh(configuration, name=None, **kwargs):
    """Open an SSH connection on a host."""
    conn = _connect_libvirt(configuration.libvirt_uri)
    hv = vl.VMMLibvirt(conn)
    domain = hv.get_domain_by_name(name)
    if not domain:
        raise VMNotFoundError(name)
    domain.exec_ssh()


def down(vmm, configuration, context="default", **kwargs):
    """Stop and remove a running environment."""

    for domain in vmm.list_domains():
        if domain.context != context:
            continue
        logger.info("x purging %s", domain.name)
        vmm.clean_up(domain)

    if configuration.network_auto_clean_up:
        vmm.network.network_obj.destroy()
