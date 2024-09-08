import unittest
from collections import namedtuple
from urllib.parse import urlparse

from virt_lightning.configuration_builder import Configuration, ConfigurationBuilder
from virt_lightning.configuration_legacy import LegacyConfiguration


class TestConfigurationBuilder(unittest.TestCase):
    def setUp(self):
        self.config = ConfigurationBuilder.create()

    def test_init(self):
        config = ConfigurationBuilder.create()
        self.assertIsNone(config._ConfigurationBuilder__source)

    def test_set_source(self):
        self.assertIsNone(self.config._ConfigurationBuilder__source)
        source = urlparse("test")
        self.config.set_source(source)
        self.assertIsNotNone(self.config._ConfigurationBuilder__source)

    def test_set_source_duplicate(self):
        self.assertIsNone(self.config._ConfigurationBuilder__source)
        source = urlparse("test")
        self.config.set_source(source)
        self.assertIsNotNone(self.config._ConfigurationBuilder__source)

        with self.assertRaises(KeyError):
            self.config.set_source(source)

    def test_invalid_build(self):
        self.assertIsNone(self.config._ConfigurationBuilder__source)

        with self.assertRaises(ValueError):
            self.config.build(LegacyConfiguration)


#
# FIXME: После проработки методов и полей класса, переписать этот тест.
#
class TestConfigurationFromBuilder(unittest.TestCase):
    def setUp(self):
        source = namedtuple("Source", ["backend", "user", "network", "registry"])
        self.config = Configuration(source(True, True, True, True))

    def test_is_true(self):
        self.assertTrue(self.config.backend)
        self.assertTrue(self.config.user)
        self.assertTrue(self.config.network)
        self.assertTrue(self.config.registry)

    def test_repr(self):
        self.assertEqual("Configuration()", repr(self.config))
