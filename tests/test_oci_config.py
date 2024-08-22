import json
import unittest
from pathlib import PosixPath

from virt_lightning.image_oci import OCIConfig


class TestOCIConfig(unittest.TestCase):
    def setUp(self):
        with PosixPath("tests/oci_data/config_from_spec.json").open() as fh:
            self.config_opt = OCIConfig(json.loads(fh.read()))
        with PosixPath("tests/oci_data/config_req.json").open() as fh:
            self.config_req = OCIConfig(json.loads(fh.read()))

    def test_required_created(self):
        self.assertIsNone(self.config_req.created)

    def test_required_author(self):
        self.assertIsNone(self.config_req.author)

    def test_required_architecture(self):
        self.assertIsNotNone(self.config_req.architecture)
        self.assertEqual(self.config_req.architecture, "amd64")

    def test_required_os(self):
        self.assertIsNotNone(self.config_req.os)
        self.assertEqual(self.config_req.os, "linux")

    def test_required_os_version(self):
        self.assertIsNone(self.config_req.os_version)

    def test_required_os_features(self):
        self.assertIsNotNone(self.config_req.os_features)
        self.assertEqual(len(self.config_req.os_features), 0)
        self.assertEqual(self.config_req.os_features, [])

    def test_required_variant(self):
        self.assertIsNone(self.config_req.variant)

    def test_required_history(self):
        self.assertIsNotNone(self.config_req.history)
        self.assertEqual(len(self.config_req.history), 0)
        self.assertEqual(self.config_req.history, [])

    def test_required_config(self):
        self.assertIsNone(self.config_req.config)

    # NOTE: Опциональные поля из примера объекта в спецификации

    def test_optional_created(self):
        self.assertIsNotNone(self.config_opt.created)

    def test_optional_author(self):
        self.assertIsNotNone(self.config_opt.author)

    def test_optional_architecture(self):
        self.assertIsNotNone(self.config_opt.architecture)
        self.assertEqual(self.config_opt.architecture, "amd64")

    def test_optional_os(self):
        self.assertIsNotNone(self.config_opt.os)
        self.assertEqual(self.config_opt.os, "linux")

    def test_optional_os_version(self):
        self.assertIsNone(self.config_opt.os_version)

    def test_optional_os_features(self):
        self.assertIsNotNone(self.config_opt.os_features)
        self.assertEqual(len(self.config_opt.os_features), 0)
        self.assertEqual(self.config_opt.os_features, [])

    def test_optional_variant(self):
        self.assertIsNone(self.config_opt.variant)

    def test_optional_history(self):
        self.assertIsNotNone(self.config_opt.history)
        self.assertEqual(len(self.config_opt.history), 3)
        self.assertGreater(len(self.config_opt.history), 0)

    def test_optional_config(self):
        self.assertIsNotNone(self.config_opt.config)
