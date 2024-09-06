import unittest
from collections import namedtuple

from virt_lightning.configuration_builder import Configuration, ConfigurationBuilder


class TestConfigurationBuilder(unittest.TestCase):
    def setUp(self):
        self.config = ConfigurationBuilder.create()

    def test_init(self):
        config = ConfigurationBuilder.create()
        self.assertIsNone(config._ConfigurationBuilder__source)

    def test_set_source(self):
        self.assertIsNone(self.config._ConfigurationBuilder__source)
        self.config.set_source("FIXME: It should be right source")
        self.assertIsNotNone(self.config._ConfigurationBuilder__source)

    def test_set_source_duplicate(self):
        self.assertIsNone(self.config._ConfigurationBuilder__source)
        self.config.set_source("FIXME: It should be right source")
        self.assertIsNotNone(self.config._ConfigurationBuilder__source)

        with self.assertRaises(KeyError):
            self.config.set_source("FIXME: It should be right source")

    def test_invalid_build(self):
        self.assertIsNone(self.config._ConfigurationBuilder__source)

        with self.assertRaises(ValueError):
            self.config.build()

    #
    # FIXME: Переделать на использование реальных объектов с данными вместо
    #        namedtuple.
    #
    def test_valid_build(self):
        source = namedtuple("Source", ["backend", "user", "network", "registry"])
        self.config.set_source(source(True, True, True, True))
        self.assertIsNotNone(self.config.build())


#
# FIXME: После проработки методов и полей класса, переписать этот тест.
#
class TestConfigurationFromBuilder(unittest.TestCase):
    def setUp(self):
        self.config = Configuration(True, True, True, True)

    def test_is_true(self):
        self.assertTrue(self.config.backend)
        self.assertTrue(self.config.user)
        self.assertTrue(self.config.network)
        self.assertTrue(self.config.registry)

    def test_repr(self):
        self.assertEqual("Configuration()", repr(self.config))
