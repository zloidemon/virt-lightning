import ipaddress
import pathlib
from unittest.mock import (
    MagicMock,
    patch,
)

import init_system.ignition
from init_system.execfile import ExecFile

from virt_lightning.disk_auxiliary_cloudinit import AuxiliaryCloudInitDisk
from virt_lightning.disk_auxiliary_ignition import AuxiliaryIgnitionDisk
from virt_lightning.disk_auxiliary_openstack import AuxiliaryOpenstackInitDisk

GATEWAY = ipaddress.ip_interface("192.168.122.1/24")


class FakeLibvirtDomain:
    def UUIDString(self):  # noqa: N802
        return "0e2b5c1a-0000-4000-8000-000000000000"


class FakeDomain:
    def __init__(self):
        self.dom = FakeLibvirtDomain()
        self.user_data = {"bootcmd": [], "runcmd": []}
        self.nics = [
            {
                "network": "default",
                "ipv4": ipaddress.ip_interface("192.168.122.10/24"),
                "mac": "52:54:00:00:00:01",
            }
        ]

    @property
    def name(self):
        return "my-vm"

    @property
    def fqdn(self):
        return "my-vm.example.org"

    @property
    def ssh_key(self):
        return "ssh-rsa AAAAtest user@example.org"

    @property
    def root_password(self):
        return "secret"


class FakeNetwork:
    dns = GATEWAY

    def get_network_gateway(self, network_name):
        return GATEWAY


class FakeMkpasswd:
    def run_cmd(self, *args, cwd=None):
        return b"$6$hashed"


def build_config_drive(disk_class):
    """
    Run the disk class and return the ISO arguments and the content of the
    generated config drive.
    """
    captured = {}

    def fake_run_cmd(self, *args, cwd=None):
        # The ISO tool is called with: -output <iso> <extra args> <source dir>
        captured["args"] = list(args[2:-1])
        source_dir = pathlib.Path(args[-1])
        captured["files"] = {
            path.relative_to(source_dir).as_posix(): path.read_text()
            for path in sorted(source_dir.rglob("*"))
            if path.is_file()
        }
        pathlib.Path(args[1]).write_bytes(b"fake-iso")
        return b""

    disk = disk_class(MagicMock(), None, FakeNetwork())
    disk.create = lambda **kwargs: MagicMock()

    with (
        patch.object(ExecFile, "run_cmd", fake_run_cmd),
        patch.object(init_system.ignition, "ExecFileMkpasswd", FakeMkpasswd),
    ):
        disk.init(FakeDomain())

    return captured["args"], captured["files"]


def test_cloudinit_config_drive():
    args, files = build_config_drive(AuxiliaryCloudInitDisk)

    assert args == ["-volid", "cidata", "-joliet", "-R"]
    assert files["user-data"].startswith("#cloud-config-jsonp\n")
    assert "instance-id: iid-my-vm" in files["meta-data"]
    assert "gateway 192.168.122.1" in files["meta-data"]
    assert "192.168.122.10/24" in files["network-config.json"]


def test_ignition_config_drive():
    args, files = build_config_drive(AuxiliaryIgnitionDisk)

    assert args[-1] == "config-2"
    assert '"version": "3.4.0"' in files["openstack/latest/user_data"]
    assert '"passwordHash": "$6$hashed"' in files["openstack/latest/user_data"]
    assert '"hostname": "my-vm.example.org"' in files["openstack/latest/meta_data.json"]


def test_openstack_config_drive():
    args, files = build_config_drive(AuxiliaryOpenstackInitDisk)

    assert args[-1] == "config-2"
    assert (
        '"public_keys": {"default": "ssh-rsa AAAAtest user@example.org"}'
        in files["openstack/latest/meta_data.json"]
    )
    assert '"admin_pass": "secret"' in files["openstack/latest/meta_data.json"]
    assert (
        '"ethernet_mac_address": "52:54:00:00:00:01"'
        in files["openstack/latest/network_data.json"]
    )
