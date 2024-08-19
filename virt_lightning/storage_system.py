import getpass
import json
import logging
import pathlib
from xml.etree import ElementTree

import libvirt

#
# NOTE: При запуске тестов consts меняется каталог по-умолчанию
#
import virt_lightning.consts as consts
from virt_lightning.consts import (
    DEFAULT_LOGGER,
    DEFAULT_VL_NAME,
    QEMU_DIR,
    ExitCode,
)
from virt_lightning.downloader_native import DownloaderNative
from virt_lightning.exceptions import (
    ImageNotFoundLocallyError,
    ImageNotFoundUpstreamError,
)

STORAGE_POOL_XML = """
<pool type='dir'>
  <name></name>
  <source>
  </source>
  <target>
    <path></path>
  </target>
</pool>
"""

USER_CREATE_STORAGE_POOL_DIR = """
You need root privilege to create the storage pool, please do:
  sudo mkdir -p {storage_dir}/upstream
  sudo chown -R {qemu_user}:{qemu_group} {storage_dir}
  sudo chown -R {user} {storage_dir}/upstream
  sudo chmod 775 /var/lib/{storage_name}
  sudo chmod 775 {storage_dir} {storage_dir}/upstream
"""

logger = logging.getLogger(DEFAULT_LOGGER)


class StorageSystem:
    def __init__(self, conn):
        self.conn = conn
        self.storage_pool_obj = None

    def create_storage_pool(self, name, directory):
        root = ElementTree.fromstring(STORAGE_POOL_XML)
        root.find("./name").text = name
        root.find("./target/path").text = str(directory)
        xml = ElementTree.tostring(root).decode()
        pool = self.conn.storagePoolDefineXML(xml, 0)
        if not pool:
            raise Exception("Failed to create pool:", name, xml)
        return pool

    @property
    def storage_dir(self):
        xml = self.storage_pool_obj.XMLDesc(0)
        root = ElementTree.fromstring(xml)
        disk_source = root.find("./target/path")
        return pathlib.PosixPath(disk_source.text)

    def init_storage_pool(self, storage_pool):
        try:
            self.storage_pool_obj = self.conn.storagePoolLookupByName(storage_pool)
        except libvirt.libvirtError as e:
            if e.get_error_code() != libvirt.VIR_ERR_NO_STORAGE_POOL:
                raise (e)

        storage_dir = pathlib.PosixPath(consts.DEFAULT_STORAGE_DIR)
        if not self.storage_pool_obj:
            self.storage_pool_obj = self.create_storage_pool(
                name=storage_pool, directory=storage_dir
            )

        try:
            full_dir = storage_dir / "upstream"
            dir_exists = full_dir.is_dir()
        except PermissionError:
            dir_exists = False

        if not dir_exists:
            qemu_dir = pathlib.PosixPath(QEMU_DIR)
            logger.error(
                USER_CREATE_STORAGE_POOL_DIR.format(  # noqa: G001
                    qemu_group=qemu_dir.group(),
                    qemu_user=qemu_dir.owner(),
                    storage_dir=self.storage_dir,
                    storage_name=DEFAULT_VL_NAME,
                    user=getpass.getuser(),
                )
            )
            exit(ExitCode.FAIL.value)

        if not self.storage_pool_obj.isActive():
            self.storage_pool_obj.create(0)

    def distro_available(self):
        path = self.storage_dir / "upstream"
        return [path.stem for path in sorted(path.glob("*.qcow2"))]

    def ensure_image_exists(self, configuration, distro):
        if distro not in self.distro_available():
            logger.debug("distro not available: %s, will be fetched", distro)
            try:
                downloader = DownloaderNative(
                    configuration,
                    self.storage_dir,
                )
                downloader.pull(distro=distro)
            except ImageNotFoundUpstreamError:
                raise ImageNotFoundLocallyError(distro) from None

    def get_distro_configuration(self, distro):
        distro_configuration_file = pathlib.PosixPath(
            f"{self.storage_dir}/upstream/{distro}.json"
        )
        if not distro_configuration_file.exists():
            return {}

        return json.load(distro_configuration_file.open("r")) or {}
