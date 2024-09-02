import unittest

from virt_lightning.configuration_registry import ConfigurationRegistry


class TestConfigurationRegistry(unittest.TestCase):
    def setUp(self):
        self.config = ConfigurationRegistry()

    def test_valid(self):
        self.assertEqual(None, self.config._ConfigurationRegistry__entrypoint)
        self.config.entrypoint = "path/to/registry"
        self.assertEqual("path/to/registry", self.config._ConfigurationRegistry__entrypoint)
        self.assertEqual("path/to/registry", self.config.entrypoint)

    def test_invalid(self):
        with self.assertRaises(TypeError):
            self.config.entrypoint = None
        with self.assertRaises(TypeError):
            self.config.entrypoint = 123

    def test_empty(self):
        with self.assertRaises(AttributeError):
            self.assertIsNone(self.config.entrypoint)

    def test_eq_invalid(self):
        config = ConfigurationRegistry()

        with self.assertRaises(AttributeError):
            self.assertEqual(self.config, config)

        config.entrypint = "example/path"
        with self.assertRaises(AttributeError):
            self.assertEqual(self.config, config)

        self.config.entrypoint = "master/path"
        config = ConfigurationRegistry()

        with self.assertRaises(AttributeError):
            self.assertEqual(self.config, config)

    def test_eq_valid(self):
        config = ConfigurationRegistry()

        config.entrypoint = "valid/path"
        self.config.entrypoint = "valid/path"

        self.assertEqual(self.config, config)
