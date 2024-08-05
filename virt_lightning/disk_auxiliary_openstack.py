import json
import pathlib
import tempfile

import yaml

from virt_lightning.execfile_iso_tools import ExecFileISOTool
from virt_lightning.idisk import IDisk


class AuxiliaryOpenstackInitDisk(IDisk):
    def __init__(self, conn):
        self.conn = conn

    def get_openstack_network_data(self, domain):
        openstack_network_data = {
            "links": [],
            "networks": [],
            "services": [{"type": "dns", "address": str(self.dns.ip)}],
        }

        for i, nic in enumerate(domain.nics):
            openstack_network_data["links"].append(
                {
                    "id": f"interface{i}",
                    "type": "phy",
                    "ethernet_mac_address": nic["mac"],
                }
            )

            gateway = self.get_network_gateway(nic["network"])
            if nic["ipv4"]:
                net_dns_nameservers = (
                    [str(self.dns.ip)] if self.dns.ip in nic["ipv4"].network else []
                )
                openstack_network_data["networks"].append(
                    {
                        "id": f"private-ipv4-{i}",
                        "type": "ipv4",
                        "link": f"interface{i}",
                        "ip_address": str(nic["ipv4"].ip),
                        "netmask": str(nic["ipv4"].netmask.exploded),
                        "routes": [
                            {
                                "network": "0.0.0.0",
                                "netmask": "0.0.0.0",
                                "gateway": str(gateway.ip),
                            }
                        ],
                        "network_id": domain.dom.UUIDString(),
                        # Workaround for CloudInit, sources.helpers.openstack read the
                        # subnet DNS from ths dns_nameservers and ignore the
                        # services key.
                        # https://opendev.org/openstack/nova/commit/4b333b989dfc778a8b61db4a1b8552e988a10471
                        "dns_nameservers": net_dns_nameservers,
                        "services": [
                            {"type": "dns", "address": ns} for ns in net_dns_nameservers
                        ],
                    }
                )
            else:
                openstack_network_data["networks"].append(
                    {
                        "id": f"private-ipv4-{i}",
                        "type": "ipv4_dhcp",
                        "link": f"interface{i}",
                        "network_id": domain.dom.UUIDString(),
                    }
                )

        return openstack_network_data

    def prepare_cloud_init_openstack_iso(self, domain):
        with tempfile.TemporaryDirectory() as base_temp_dir:
            temp_dir = pathlib.Path(base_temp_dir)
            cd_dir = temp_dir / "cd_dir"
            cd_dir.mkdir()

            openstack_meta_data = {
                "availability_zone": "nova",
                "files": [],
                "hostname": domain.fqdn or domain.name,
                "launch_index": 0,
                "local-hostname": domain.name,
                "name": domain.name,
                "meta": {},
                "public_keys": {"default": domain.ssh_key},
                "uuid": domain.dom.UUIDString(),
                "admin_pass": domain.root_password,
            }

            openstack_dir = cd_dir / "openstack" / "latest"
            openstack_dir.mkdir(parents=True)

            openstack_metadata_file = openstack_dir / "meta_data.json"
            with openstack_metadata_file.open("w") as fd:
                fd.write(json.dumps(openstack_meta_data))

            openstack_networkdata_file = openstack_dir / "network_data.json"
            with openstack_networkdata_file.open("w") as fd:
                fd.write(json.dumps(self.get_openstack_network_data(domain)))

            openstack_userdata_file = openstack_dir / "user_data"
            with openstack_userdata_file.open("w") as fd:
                fd.write("#cloud-config\n")
                fd.write(yaml.dump(domain.user_data, Dumper=yaml.Dumper))

            cidata_file = temp_dir / f"{domain.name}-cidata.iso"
            ExecFileISOTool().run_cmd(
                "-output",
                cidata_file.name,
                "-ldots",
                "-allow-lowercase",
                "-allow-multidot",
                "-l",
                "-publisher",
                "virt-lighting",
                "-quiet",
                "-J",
                "-r",
                "-V",
                "config-2",
                str(cd_dir),
                cwd=str(temp_dir),
            )

            cdrom = self.create_disk(name=cidata_file.stem, size=1)
            with cidata_file.open("br") as fd:
                st = self.conn.newStream(0)
                cdrom.upload(st, 0, 1024 * 1024)
                st.send(fd.read())
                st.finish()
            return cdrom
