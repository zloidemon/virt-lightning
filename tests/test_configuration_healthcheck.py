import unittest

from virt_lightning.configuration_healthcheck import ConfigurationHealthcheck


class TestConfigurationHealthcheck(unittest.TestCase):
    def setUp(self):
        self.config = ConfigurationHealthcheck()

    def test_interval_valid(self):
        self.config.interval = 1
        self.assertEqual(1, self.config._ConfigurationHealthcheck__interval)

    def test_interval_invalid(self):
        with self.assertRaises(ValueError):
            self.config.interval = 0
        with self.assertRaises(ValueError):
            self.config.interval = -1

    def test_timeout_valid(self):
        self.config.timeout = 1
        self.assertEqual(1, self.config._ConfigurationHealthcheck__timeout)

    def test_timeout_invalid(self):
        with self.assertRaises(ValueError):
            self.config.timeout = 0
        with self.assertRaises(ValueError):
            self.config.timeout = -1

    def test_start_period_valid(self):
        self.config.start_period = 1
        self.assertEqual(1, self.config._ConfigurationHealthcheck__start_period)
        self.config.start_period = 0
        self.assertEqual(0, self.config._ConfigurationHealthcheck__start_period)

    def test_start_period_invalid(self):
        with self.assertRaises(ValueError):
            self.config.start_period = -1

    def test_start_interval_valid(self):
        self.config.start_interval = 1
        self.assertEqual(1, self.config._ConfigurationHealthcheck__start_interval)
        self.config.start_interval = 0
        self.assertEqual(0, self.config._ConfigurationHealthcheck__start_interval)

    def test_start_inteval_invalid(self):
        with self.assertRaises(ValueError):
            self.config.start_interval = -1

    def test_eq_default(self):
        self.assertEqual(ConfigurationHealthcheck(), ConfigurationHealthcheck())

    def test_eq(self):
        config_1 = ConfigurationHealthcheck()

        self.assertEqual(self.config, config_1)

        config_1.interval = 31
        self.assertNotEqual(self.config, config_1)

        config_1.interval = 30
        self.assertEqual(self.config, config_1)

        config_1.timeout = 31
        self.assertNotEqual(self.config, config_1)

        config_1.timeout = 30
        self.assertEqual(self.config, config_1)

        config_1.start_period = 30
        self.assertNotEqual(self.config, config_1)

        config_1.start_period = 0
        self.assertEqual(self.config, config_1)

        config_1.start_interval = 0
        self.assertNotEqual(self.config, config_1)

        config_1.start_interval = 5
        self.assertEqual(self.config, config_1)

        config_1.retries = 5
        self.assertNotEqual(self.config, config_1)

        config_1.retries = 3
        self.assertEqual(self.config, config_1)
