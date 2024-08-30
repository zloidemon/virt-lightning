import unittest

from virt_lightning.image_oci_build import OCIImageBuild
from virt_lightning.configuration_healthcheck import ConfigurationHealthcheck
from virt_lightning.healthcheck import Healthcheck


class TestOCIBuildImageHealthcheck(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.builder = OCIImageBuild(self.image_name)
        self.default_config = ConfigurationHealthcheck(30, 30, 0, 5, 3)

    def test_valid(self):
        self.builder.healthcheck("true")
        valid = Healthcheck("true", self.default_config)
        self.assertEqual(valid, self.builder._OCIImageBuild__healthcheck)

    def test_duplicate(self):
        self.builder.healthcheck("true")
        with self.assertRaises(KeyError):
            self.builder.healthcheck("true")

    def test_wrong_command_type(self):
        with self.assertRaises(TypeError):
            self.builder.healthcheck(None)
        with self.assertRaises(TypeError):
            self.builder.healthcheck(1234)
        with self.assertRaises(TypeError):
            self.builder.healthcheck(4.4)

    def test_empty_command(self):
        with self.assertRaises(ValueError):
            self.builder.healthcheck("")

    def test_wrong_options_type(self):
        for value in [None, "0", 1.3]:
            with self.assertRaises(TypeError):
                self.builder.healthcheck("test", interval=value)
            with self.assertRaises(TypeError):
                self.builder.healthcheck("test", timeout=value)
            with self.assertRaises(TypeError):
                self.builder.healthcheck("test", start_period=value)
            with self.assertRaises(TypeError):
                self.builder.healthcheck("test", start_interval=value)
            with self.assertRaises(TypeError):
                self.builder.healthcheck("test", retries=value)

    def test_wrong_option_negative(self):
        with self.assertRaises(ValueError):
            self.builder.healthcheck("test", interval=-1)
        with self.assertRaises(ValueError):
            self.builder.healthcheck("test", timeout=-2)
        with self.assertRaises(ValueError):
            self.builder.healthcheck("test", start_period=-3)
        with self.assertRaises(ValueError):
            self.builder.healthcheck("test", start_interval=-4)
        with self.assertRaises(ValueError):
            self.builder.healthcheck("test", retries=-5)
