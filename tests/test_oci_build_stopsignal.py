import unittest

from virt_lightning.consts import SignalShutdown
from virt_lightning.image_oci_build import OCIImageBuild


class TestOCIBuildImageStopSignal(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.builder = OCIImageBuild(self.image_name)

    def test_valid(self):
        sig = SignalShutdown.ACPI

        self.assertEqual(None, self.builder._OCIImageBuild__stopsignal)

        self.builder.stopsignal(sig)

        self.assertEqual(SignalShutdown.ACPI, self.builder._OCIImageBuild__stopsignal)

    def test_duplicate(self):
        self.builder.stopsignal(SignalShutdown.ACPI)

        with self.assertRaises(KeyError):
            self.builder.stopsignal(SignalShutdown.ACPI)
        with self.assertRaises(KeyError):
            self.builder.stopsignal(SignalShutdown.AGENT)

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            self.builder.stopsignal(None)
        with self.assertRaises(TypeError):
            self.builder.stopsignal("ACPI")
        with self.assertRaises(TypeError):
            self.builder.stopsignal("acpi")
        with self.assertRaises(TypeError):
            self.builder.stopsignal(1345)
        with self.assertRaises(TypeError):
            self.builder.stopsignal(0x1)
