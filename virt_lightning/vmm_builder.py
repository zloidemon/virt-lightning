from urllib.parse import urlparse

import libvirt

from virt_lightning.exceptions import CannotConnectToLibvirtError


class VMMBuilder:
    def __init__(self, configuration):
        self.__configuration = configuration
        self.__vmm = None
        self.__storage = None
        self.__connection = None

    def connect(self):
        self.__connection = self.__connect_libvirt()

        vmm = self.__vmm(self.__connection)
        vmm.storage.init_storage_pool(self.__configuration.storage_pool)
        vmm.network.init_network(
            self.__configuration.network_name,
            self.__configuration.network_cidr,
        )

        return vmm

    def __connect_libvirt(self):
        uri = self.__configuration.libvirt_uri
        try:
            if urlparse(uri).netloc == "":
                return libvirt.open(uri)
            else:
                raise NotImplementedError("Only local access allowed")
        except libvirt.libvirtError as e:
            if e.get_error_code() == libvirt.VIR_ERR_AUTH_UNAVAILABLE:
                raise CannotConnectToLibvirtError() from None
            raise

    def set_network(self, network):
        self.__network = network
        return self

    def set_storage(self, storage):
        self.__storage = storage
        return self

    def set_vmm(self, vmm):
        self.__vmm = vmm
        return self
