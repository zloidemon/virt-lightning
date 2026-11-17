import ipaddress

from virt_lightning.domain_metadata import build_metadata


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
    dns = ipaddress.ip_interface("192.168.122.1/24")

    def get_network_gateway(self, network_name):
        return ipaddress.ip_interface("192.168.122.1/24")


def test_build_metadata():
    metadata = build_metadata(FakeDomain(), FakeNetwork())

    assert metadata.name == "my-vm"
    assert metadata.uuid == "0e2b5c1a-0000-4000-8000-000000000000"
    assert metadata.fqdn == "my-vm.example.org"
    assert metadata.hostname == "my-vm.example.org"
    assert metadata.user_data == {"bootcmd": [], "runcmd": []}
    assert metadata.ssh_key == "ssh-rsa AAAAtest user@example.org"
    assert metadata.root_password == "secret"
    assert metadata.dns == ipaddress.ip_address("192.168.122.1")


def test_build_metadata_nics():
    metadata = build_metadata(FakeDomain(), FakeNetwork())

    assert len(metadata.nics) == 1
    nic = metadata.nics[0]
    assert nic.name == "eth0"
    assert nic.mac == "52:54:00:00:00:01"
    assert nic.ipv4 == ipaddress.ip_interface("192.168.122.10/24")
    assert nic.network == "default"
    assert nic.gateway == ipaddress.ip_address("192.168.122.1")


def test_build_metadata_without_network():
    class NoNetwork:
        dns = None

    metadata = build_metadata(FakeDomain(), NoNetwork())

    assert metadata.dns is None
    assert metadata.nics[0].gateway is None
