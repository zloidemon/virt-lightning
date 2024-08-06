import getpass
import logging
import pathlib
from xml.etree import ElementTree

import libvirt

import virt_lightning.consts as consts
from virt_lightning.templates import (
    STORAGE_POOL_XML,
    USER_CREATE_STORAGE_POOL_DIR,
)

logger = logging.getLogger("virt_lightning")


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
            qemu_dir = pathlib.PosixPath(consts.QEMU_DIR)
            logger.error(
                USER_CREATE_STORAGE_POOL_DIR.format(  # noqa: G001
                    user=getpass.getuser(),
                    qemu_user=qemu_dir.owner(),
                    qemu_group=qemu_dir.group(),
                    storage_dir=self.storage_dir,
                )
            )
            exit(consts.ExitCode.FAIL.value)

        if not self.storage_pool_obj.isActive():
            self.storage_pool_obj.create(0)
