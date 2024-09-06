import unittest
from unittest.mock import patch

from virt_lightning.icli import ICLIcmd


class TestICLIcmd(unittest.TestCase):
    @patch.multiple(ICLIcmd, __abstractmethods__=set())
    def setUp(self):
        self.cli = ICLIcmd("x", "y")

    def test_arguments(self):
        self.assertIsNone(self.cli.arguments())

    def test_context(self):
        self.assertIsNone(self.cli.context("hello"))

    @patch.multiple(ICLIcmd, __abstractmethods__=set())
    def test_run(self):
        self.assertIsNone(ICLIcmd.run())
