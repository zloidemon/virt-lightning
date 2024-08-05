import logging
import pathlib
import sys
from abc import (
    ABCMeta,
    abstractmethod,
)
from xml.etree import ElementTree

import libvirt

import virt_lightning.consts as consts
from virt_lightning.templates import STORAGE_VOLUME_XML

logger = logging.getLogger("virt_lightning")


#
# Общий интерфейс для работы с дисками
#
class IDisk(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, conn):
        pass

    @abstractmethod
    def init(self, domain):
        pass

    def create(self, name, size=None, backing_on=None):
        backing_file = None
        min_size = 0
        if backing_on:
            backing_file = pathlib.PosixPath(
                f"{self.get_storage_dir()}/upstream/{backing_on}.qcow2"
            )
            min_size = self.get_qcow_virtual_size(backing_file)
        disk_path = pathlib.PosixPath(f"{self.get_storage_dir()}/{name}.qcow2")

        if "/" in name:
            raise TypeError
        if not size:
            size = 20
        if size < min_size:
            size = min_size
            logger.debug(
                "Increasing the size of the image to match the backing image size: %s (%dGB)",
                str(disk_path),
                size,
            )

        logger.debug("create_disk: %s (%dGB)", str(disk_path), size)
        root = ElementTree.fromstring(STORAGE_VOLUME_XML)
        root.find("./name").text = disk_path.name
        root.find("./capacity").text = str(size)
        root.find("./target/path").text = str(disk_path)

        if backing_file:
            backing = ElementTree.SubElement(root, "backingStore")
            ElementTree.SubElement(backing, "path").text = str(backing_file)
            ElementTree.SubElement(backing, "format").attrib = {"type": "qcow2"}

        xml = ElementTree.tostring(root).decode()
        try:
            return self.storage_pool_obj.createXML(xml)
        except libvirt.libvirtError as e:
            if e.get_error_code() == libvirt.VIR_ERR_STORAGE_VOL_EXIST:
                logger.error(
                    f"A volume image already exists and prevent the creation "
                    f" of a new one. You can remove it with the following "
                    f"command:\n"
                    f"  sudo virsh vol-delete --pool "
                    f"{self.storage_pool_obj.name()} {name}.qcow2"
                )
                sys.exit(consts.ExitCode.FAIL.value)
            raise
