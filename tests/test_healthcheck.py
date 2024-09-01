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

    def test_eq_command(self):
        healthcheck = Healthcheck("true", self.config)
        self.assertEqual(self.healthcheck.command, healthcheck.command)

    def test_not_eq_command(self):
        healthcheck = Healthcheck("rtrue", self.config)
        self.assertNotEqual(self.healthcheck.command, healthcheck.command)

    def test_eq_config(self):
        healthcheck = Healthcheck("true", self.config)
        self.assertEqual(self.config, healthcheck.configuration)

    def test_not_eq_config(self):
        config = ConfigurationHealthcheck()
        config.interval = 3
        healthcheck = Healthcheck("true", config)
        self.assertNotEqual(self.healthcheck, healthcheck)
