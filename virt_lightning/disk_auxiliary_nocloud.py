import pathlib
import tempfile

import yaml

from virt_lightning.execfile_iso_tools import ExecFileISOTool
from virt_lightning.idisk import IDisk
from virt_lightning.templates import META_DATA_ENI


class AuxiliaryCloudInitDisk(IDisk):
    def __init__(self, conn):
        self.conn = conn

    def init(self, domain):
        self._network_meta = {"config": "disabled"}
        network_config = []
        for i, nic in enumerate(domain.nics):
            gateway = self.get_network_gateway(nic["network"])
            if nic["ipv4"]:
                network_config.append(
                    {
                        "type": "physical",
                        "name": f"eth{i}",
                        "mac_address": nic["mac"],
                        "subnets": [
                            {
                                "type": "static",
                                "address": str(nic["ipv4"]),
                                "gateway": str(gateway.ip),
                                "dns_nameservers": [str(gateway.ip)],
                            }
                        ],
                    }
                )
            else:
                network_config.append(
                    {
                        "type": "physical",
                        "name": f"eth{i}",
                        "mac_address": nic["mac"],
                        "subnets": [{"type": "dhcp"}],
                    }
                )
        domain._network_meta = {"version": 1, "config": network_config}

        with tempfile.TemporaryDirectory() as base_temp_dir:
            temp_dir = pathlib.Path(base_temp_dir)
            cd_dir = temp_dir / "cd_dir"
            cd_dir.mkdir()
            user_data_file = cd_dir / "user-data"
            with user_data_file.open("w") as fd:
                fd.write("#cloud-config\n")
                fd.write(yaml.dump(domain.user_data, Dumper=yaml.Dumper))
            meta_data_file = cd_dir / "meta-data"
            with meta_data_file.open("w") as fd:
                fd.write(
                    META_DATA_ENI.format(
                        name=domain.name,
                        ipv4=str(domain.ipv4.ip),
                        gateway=str(self.gateway.ip),
                        network=str(self.network),
                    )
                )
            network_config_file = cd_dir / "network-config"
            with network_config_file.open("w") as fd:
                fd.write(yaml.dump(domain._network_meta, Dumper=yaml.Dumper))

            cidata_file = temp_dir / f"{domain.name}-cidata.iso"
            ExecFileISOTool().run_cmd(
                "-output",
                cidata_file.name,
                "-volid",
                "cidata",
                "-joliet",
                "-R",
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
