import unittest

from virt_lightning.configuration_tcpip import ConfigurationTCPIP


class TestConfigurationTCPIP(unittest.TestCase):
    def setUp(self):
        self.config = ConfigurationTCPIP()

    def test_valid_name(self):
        self.assertEqual(None, self.config._ConfigurationTCPIP__name)
        self.config.name = "network"
        self.assertEqual("network", self.config._ConfigurationTCPIP__name)
        self.assertEqual("network", self.config.name)

    def test_invalid_name(self):
        with self.assertRaises(TypeError):
            self.config.name = None
        with self.assertRaises(TypeError):
            self.config.name = 123

    def test_empty_name(self):
        with self.assertRaises(AttributeError):
            self.assertIsNone(self.config.name)

    def test_empty_cidr(self):
        with self.assertRaises(AttributeError):
            self.assertIsNone(self.config.cidr)

    def test_valid_cidr(self):
        self.assertEqual(None, self.config._ConfigurationTCPIP__cidr)
        self.config.cidr = "192.168.123.0/24"
        self.assertEqual("192.168.123.0/24", self.config._ConfigurationTCPIP__cidr)
        self.assertEqual("192.168.123.0/24", self.config.cidr)

    def test_invalid_cidr(self):
        with self.assertRaises(TypeError):
            self.config.cidr = None
        with self.assertRaises(TypeError):
            self.config.cidr = 123

    def test_valid_auto_cleanup(self):
        self.assertIsNone(self.config._ConfigurationTCPIP__clean)
        self.config.auto_cleanup = True
        self.assertTrue(True, self.config._ConfigurationTCPIP__clean)
        self.assertTrue(True, self.config.auto_cleanup)
        self.config.auto_cleanup = False
        self.assertFalse(self.config._ConfigurationTCPIP__clean)
        self.assertFalse(self.config.auto_cleanup)

    def test_invalid_auto_cleanup(self):
        with self.assertRaises(TypeError):
            self.config.auto_cleanup = None
        with self.assertRaises(TypeError):
            self.config.auto_cleanup = 123
        with self.assertRaises(TypeError):
            self.config.auto_cleanup = "True"
        with self.assertRaises(TypeError):
            self.config.auto_cleanup = "False"

    def test_empty_auto_cleanup(self):
        with self.assertRaises(AttributeError):
            self.assertIsNone(self.config.auto_cleanup)

    def test_eq_invalid_name(self):
        config = ConfigurationTCPIP()

        config.name = "network"
        with self.assertRaises(AttributeError):
            self.assertEqual(self.config, config)

        self.config.name = "network2"
        config = ConfigurationTCPIP()

        with self.assertRaises(AttributeError):
            self.assertEqual(self.config, config)

    def test_eq_invalid_cidr(self):
        config = ConfigurationTCPIP()

        config.cidr = "192.168.122.0/24"
        with self.assertRaises(AttributeError):
            self.assertEqual(self.config, config)

        self.config.cidr = "192.168.123.0/24"
        config = ConfigurationTCPIP()

        with self.assertRaises(AttributeError):
            self.assertEqual(self.config, config)

    def test_eq_invalid_auto_cleanup(self):
        config = ConfigurationTCPIP()

        config.auto_cleanup = True
        with self.assertRaises(AttributeError):
            self.assertEqual(self.config, config)

        self.config.auto_cleanup = False
        config = ConfigurationTCPIP()

        with self.assertRaises(AttributeError):
            self.assertEqual(self.config, config)

    def test_eq_invalid_empty(self):
        config = ConfigurationTCPIP()

        with self.assertRaises(AttributeError):
            self.assertEqual(self.config, config)

    def test_eq_invalid_all(self):
        config = ConfigurationTCPIP()

        config.name = "network"
        config.cidr = "192.168.123.0/24"
        config.auto_cleanup = False

        self.config.name = "network2"
        self.config.cidr = "192.168.122.0/24"
        self.config.auto_cleanup = True

        self.assertNotEqual(self.config, config)

    def test_eq_valid(self):
        config = ConfigurationTCPIP()

        config.name = "network"
        config.cidr = "192.168.123.0/24"
        config.auto_cleanup = True

        self.config.name = "network"
        self.config.cidr = "192.168.123.0/24"
        self.config.auto_cleanup = True

        self.assertEqual(self.config, config)
