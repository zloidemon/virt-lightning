import unittest

from virt_lightning.configuration_healthcheck import ConfigurationHealthcheck
from virt_lightning.healthcheck import Healthcheck


class TestCommandHealthcheck(unittest.TestCase):
    def setUp(self):
        self.config = ConfigurationHealthcheck()
        self.healthcheck = Healthcheck("true", self.config)

    def test_valid(self):
        self.assertEqual("true", self.healthcheck.command)
        self.assertEqual("true", self.healthcheck._Healthcheck__cmd)

    def test_invalid_retires(self):
        with self.assertRaises(ValueError):
            self.config.retries = 0
        with self.assertRaises(ValueError):
            self.config.retries = -1
        with self.assertRaises(ValueError):
            self.config.retries = -10

    def test_init_value_retries(self):
        self.assertEqual(3, self.config._ConfigurationHealthcheck__retries)
        self.assertEqual(3, self.config.retries)
        self.assertEqual(
            self.config._ConfigurationHealthcheck__retries,
            self.config.retries
        )

    def test_valid_retries(self):
        self.config.retries = 1
        self.assertGreater(self.config._ConfigurationHealthcheck__retries, 0)
        self.assertEqual(1, self.config._ConfigurationHealthcheck__retries)

    def test_eq_command(self):
        healthcheck = Healthcheck("true", self.config)
        self.assertEqual(self.healthcheck.command, healthcheck.command)

    def test_not_eq_command(self):
        healthcheck = Healthcheck("rtrue", self.config)
        self.assertNotEqual(self.healthcheck.command, healthcheck.command)
        self.assertNotEqual(self.healthcheck, healthcheck)

    def test_eq_config(self):
        healthcheck = Healthcheck("true", self.config)
        self.assertEqual(self.config, healthcheck.configuration)

    def test_not_eq_config(self):
        config = ConfigurationHealthcheck()
        config.interval = 3
        healthcheck = Healthcheck("true", config)
        self.assertNotEqual(self.healthcheck, healthcheck)
