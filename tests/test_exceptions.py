import unittest

from virt_lightning.exceptions import (
    CannotConnectToLibvirtError,
    ImageNotFoundLocallyError,
    ImageNotFoundUpstreamError,
    VMNotFoundError,
    VMNotRunningError,
)


class TestExceptions(unittest.TestCase):
    def test_cannot_connect_to_libvirt_error(self):
        with self.assertRaises(CannotConnectToLibvirtError):
            raise CannotConnectToLibvirtError

    def test_image_not_found_locally_error(self):
        with self.assertRaises(ImageNotFoundLocallyError) as ctx:
            raise ImageNotFoundLocallyError("Test local error message")

        self.assertEqual("Test local error message", ctx.exception.name)

    def test_image_not_found_upstream_error(self):
        with self.assertRaises(ImageNotFoundUpstreamError) as ctx:
            raise ImageNotFoundUpstreamError("Test upstream error message")

        self.assertEqual("Test upstream error message", ctx.exception.name)

    def test_vm_not_found_error(self):
        with self.assertRaises(VMNotFoundError) as ctx:
            raise VMNotFoundError("Test vm not found message")

        self.assertEqual("Test vm not found message", ctx.exception.name)

    def test_vm_not_running_error(self):
        with self.assertRaises(VMNotRunningError) as ctx:
            raise VMNotRunningError("Test vm running message")

        self.assertEqual("Test vm running message", ctx.exception.name)
