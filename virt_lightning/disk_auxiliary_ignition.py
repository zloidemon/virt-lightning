import json
import pathlib
import tempfile

from virt_lightning.execfile_iso_tools import ExecFileISOTool
from virt_lightning.execfile_mkpasswd import ExecFileMkpasswd
from virt_lightning.idisk import IDisk


class AuxiliaryIgnitionDisk(IDisk):
    def __init__(self, conn, storage, network):
        self.conn = conn
        self.storage = storage
        self.network = network

    def __ignition_file(self, domain):
        data = {"ignition": {"version": "3.4.0"}}
        root_user = {
            "name": "root",
            "passwordHash": self.__mkpasswd(domain.root_password),
            "sshAuthorizedKeys": [domain.ssh_key],
        }
        data["passwd"] = {
            "users": [root_user],
        }
        data["storage"] = {
            "files": [
                {
                    "path": "/etc/ssh/sshd_config.d/20-enable-passwords.conf",
                    "contents": {
                        "compression": "",
                        "source": "data:,PasswordAuthentication%20yes%0A",
                    },
                    "mode": 420,
                },
            ]
        }

        return json.dumps(data)

    def __mkpasswd(self, password):
        hashed = ExecFileMkpasswd().run_cmd("-m", "yescrypt", password)
        return hashed.decode().strip()

    def init(self, domain):
        with tempfile.TemporaryDirectory() as base_temp_dir:
            temp_dir = pathlib.Path(base_temp_dir)
            cd_dir = temp_dir / "cd_dir"
            cd_dir.mkdir()

            openstack_dir = cd_dir / "openstack" / "latest"
            openstack_dir.mkdir(parents=True)

            user_data_file = openstack_dir / "user_data"
            with user_data_file.open("w") as fd:
                fd.write(self.__ignition_file(domain))

            openstack_meta_data = {
                "availability_zone": "nova",
                "files": [],
                "hostname": domain.fqdn or domain.name,
                "launch_index": 0,
                "local-hostname": domain.name,
                "name": domain.name,
                "meta": {},
                "uuid": domain.dom.UUIDString(),
            }

            openstack_metadata_file = openstack_dir / "meta_data.json"
            with openstack_metadata_file.open("w") as fd:
                fd.write(json.dumps(openstack_meta_data))

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

            cdrom = self.create(name=cidata_file.stem, size=1)
            with cidata_file.open("br") as fd:
                st = self.conn.newStream(0)
                cdrom.upload(st, 0, 1024 * 1024)
                st.send(fd.read())
                st.finish()
            return cdrom
