import pathlib

from virt_lightning.templates import META_DATA_ENI
from virt_lightning.idisk import IDisk
from virt_lightning.execfile_iso_tools import ExecFileISOTool


class AuxiliaryCloudInitDisk(IDisk):
    def prepare_cloud_init_nocloud_iso(self, domain):
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
            run_cmd(
                [
                    str(ExecFileISOTool().entrypoint),
                    "-output",
                    cidata_file.name,
                    "-volid",
                    "cidata",
                    "-joliet",
                    "-R",
                    str(cd_dir),
                ],
                cwd=str(temp_dir),
            )

            cdrom = self.create_disk(name=cidata_file.stem, size=1)
            with cidata_file.open("br") as fd:
                st = self.conn.newStream(0)
                cdrom.upload(st, 0, 1024 * 1024)
                st.send(fd.read())
                st.finish()
            return cdrom


class AuxiliaryOpenstackInitDisk(IDisk):
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
            run_cmd(
                [
                    str(ExecFileISOTool().entrypoint),
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
                ],
                cwd=str(temp_dir),
            )

            cdrom = self.create_disk(name=cidata_file.stem, size=1)
            with cidata_file.open("br") as fd:
                st = self.conn.newStream(0)
                cdrom.upload(st, 0, 1024 * 1024)
                st.send(fd.read())
                st.finish()
            return cdrom

