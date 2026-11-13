import asyncio
from urllib.parse import urlparse

import libvirt

from virt_lightning.exceptions import CannotConnectToLibvirtError


def _register_aio_virt_impl(loop):
    # Ensure we may call shell.up() multiple times
    # from the same asyncio program.
    try:
        loop = loop or asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop not in _register_aio_virt_impl.aio_virt_bindinds:
        try:
            import libvirtaio

            libvirtaio.virEventRegisterAsyncIOImpl(loop=loop)
        except ImportError:
            libvirt.virEventRegisterDefaultImpl()
        _register_aio_virt_impl.aio_virt_bindinds[loop] = True
	return loop


_register_aio_virt_impl.__dict__["aio_virt_bindinds"] = {}


class VMMBuilder:
    def __init__(self, configuration):
        self.__configuration = configuration
        self.__vmm = None
        self.__storage = None
        self.__connection = None

    def connect(self):
        self.__connection = self.__connect_libvirt()
        #
        # FIXME: Перенести константы в конфигурацию
        #
        self.__connection.setKeepAlive(interval=5, count=3)

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

            def libvirt_callback(userdata, err):
                pass

            libvirt.registerErrorHandler(f=libvirt_callback, ctx=None)

            if urlparse(uri).netloc == "":
                _register_aio_virt_impl(loop=asyncio.get_event_loop())
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
