import unittest

from virt_lightning.configuration_backend import ConfigurationBackend


class TestConfigurationBackend(unittest.TestCase):
    def setUp(self):
        self.config = ConfigurationBackend()

    def test_valid_entrypoint(self):
        self.assertEqual(None, self.config._ConfigurationBackend__entrypoint)
        self.config.entrypoint = "path/to/registry"
        self.assertEqual("path/to/registry", self.config._ConfigurationBackend__entrypoint)
        self.assertEqual("path/to/registry", self.config.entrypoint)

    def test_valid_storage(self):
        self.assertEqual(None, self.config._ConfigurationBackend__storage)
        self.config.storage = "path/to/storage"
        self.assertEqual("path/to/storage", self.config._ConfigurationBackend__storage)
        self.assertEqual("path/to/storage", self.config.storage)

    def test_invalid_entrypoint(self):
        with self.assertRaises(TypeError):
            self.config.entrypoint = None
        with self.assertRaises(TypeError):
            self.config.entrypoint = 123

    def test_invalid_storage(self):
        with self.assertRaises(TypeError):
            self.config.storage = None
        with self.assertRaises(TypeError):
            self.config.storage = 123

    def test_empty(self):
        with self.assertRaises(AttributeError):
            self.assertIsNone(self.config.entrypoint)
        with self.assertRaises(AttributeError):
            self.assertIsNone(self.config.storage)

    def test_eq_invalid_entrypoint(self):
        config = ConfigurationBackend()

        config.entrypoint = "example/path"
        with self.assertRaises(AttributeError):
            self.assertEqual(self.config, config)

        self.config.entrypoint = "master/path"
        config = ConfigurationBackend()

        with self.assertRaises(AttributeError):
            self.assertEqual(self.config, config)

    def test_eq_invalid_storage(self):
        config = ConfigurationBackend()

        config.storage = "example/path/storage"
        with self.assertRaises(AttributeError):
            self.assertEqual(self.config, config)

        self.config.storage = "master/path/storage"
        config = ConfigurationBackend()

        with self.assertRaises(AttributeError):
            self.assertEqual(self.config, config)

    def test_eq_invalid_empty(self):
        config = ConfigurationBackend()

        with self.assertRaises(AttributeError):
            self.assertEqual(self.config, config)

    def test_eq_invalid_all(self):
        config = ConfigurationBackend()

        config.entrypoint = "example/path"
        config.storage = "example/path/storage"

        self.config.entrypoint = "master/path"
        self.config.storage = "master/path/storage"

        self.assertNotEqual(self.config, config)

    def test_eq_valid(self):
        config = ConfigurationBackend()

        config.entrypoint = "valid/path"
        config.storage = "storage"

        self.config.entrypoint = "valid/path"
        self.config.storage = "storage"

        self.assertEqual(self.config, config)
