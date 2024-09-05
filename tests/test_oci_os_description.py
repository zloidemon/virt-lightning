import unittest

from virt_lightning.consts import OperationSystem
from virt_lightning.image_oci_os import OCIOSDescription


class TestOCIOSDescriptionRequired(unittest.TestCase):
    def test_architecture(self):
        platform = OCIOSDescription({"architecture": "e2k", "os": "linux"})
        self.assertEqual(platform.architecture, "e2k")

    def test_architecture_fail(self):
        platform = OCIOSDescription({"os": "linux"})
        with self.assertRaises(KeyError):
            self.assertEqual(platform.architecture, "e2k")

    def test_os(self):
        platform = OCIOSDescription({"architecture": "e2k", "os": "linux"})
        self.assertEqual(OperationSystem.LINUX, platform.os)

    def test_os_fail(self):
        platform = OCIOSDescription({"architecture": "e2k"})
        with self.assertRaises(KeyError):
            self.assertEqual(OperationSystem.LINUX, platform.os)

    def test_features(self):
        platform = OCIOSDescription({"architecture": "e2k"})
        with self.assertRaises(NotImplementedError):
            self.assertIsNotNone(platform.features)


class TestOCIOSDescriptionOptional(unittest.TestCase):
    def test_variant_none(self):
        platform = OCIOSDescription({"architecture": "e2k"})
        self.assertIsNone(platform.variant)

    def test_variant(self):
        platform = OCIOSDescription({"architecture": "amd64", "variant": "v1"})
        self.assertEqual("v1", platform.variant)
        self.assertEqual("amd64", platform.architecture)

    def test_os_version_none(self):
        platform = OCIOSDescription({"os": "windows"})
        self.assertEqual(OperationSystem.WINDOWS, platform.os)
        self.assertIsNone(platform.os_version)

    def test_os_version(self):
        platform = OCIOSDescription({"os": "windows", "os.version": "10.0.14393.1066"})
        self.assertEqual(OperationSystem.WINDOWS, platform.os)
        self.assertEqual("10.0.14393.1066", platform.os_version)

    def test_os_features_none(self):
        platform = OCIOSDescription({"os": "windows"})
        self.assertEqual(OperationSystem.WINDOWS, platform.os)
        self.assertListEqual([], platform.os_features)

    def test_os_features(self):
        platform = OCIOSDescription({"os": "windows", "os.features": ["win32k.sys"]})
        self.assertEqual(OperationSystem.WINDOWS, platform.os)
        self.assertListEqual(["win32k.sys"], platform.os_features)
