import unittest
from unittest.mock import patch

from virt_lightning.ihealthcheck import IHealthcheck


class TestIHealthcheck(unittest.TestCase):
    @patch.multiple(IHealthcheck, __abstractmethods__=set())
    def setUp(self):
        self.healthcheck = IHealthcheck("cmd", "configuration")

    def test_command(self):
        self.assertIsNone(self.healthcheck.command)

    def test_configuration(self):
        self.assertIsNone(self.healthcheck.configuration)

    def test_repr(self):
        self.assertEqual("Healthcheck(command=None)", repr(self.healthcheck))
