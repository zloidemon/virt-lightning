import unittest
from pathlib import PosixPath
from unittest.mock import Mock

from virt_lightning.configuration_load_file import ConfigurationLegacyLoadFile


class TestConfigurationLegacyLoadFile(unittest.TestCase):
    def setUp(self):
        self.config = ConfigurationLegacyLoadFile()

    def test_invalid_load_from(self):
        with self.assertRaises(TypeError):
            self.config.load_from("xxx")
        with self.assertRaises(TypeError):
            self.config.load_from("/path/to/file.toml")
        with self.assertRaises(TypeError):
            self.config.load_from(None)
        with self.assertRaises(TypeError):
            self.config.load_from(1234)

    def test_valid_load_from(self):
        self.assertIsNone(self.config._ConfigurationLegacyLoadFile__filename)
        mock_refresh = Mock(return_value=None)
        mock_config = PosixPath("/path/to/file.toml")
        self.config._ConfigurationLegacyLoadFile__refresh = mock_refresh
        self.config.load_from(mock_config)
        self.assertIsNotNone(self.config._ConfigurationLegacyLoadFile__filename)
        self.assertEqual(mock_config, self.config._ConfigurationLegacyLoadFile__filename)
