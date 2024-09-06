import unittest
from unittest.mock import patch

from virt_lightning.ijsonb import IJsonb


class TestIJsonb(unittest.TestCase):
    @patch.multiple(IJsonb, __abstractmethods__=set())
    def setUp(self):
        self.config = IJsonb()

    def test_add(self):
        self.assertIsNone(self.config.add("path", "value"))

    def test_remove(self):
        self.assertIsNone(self.config.remove("path"))

    def test_replace(self):
        self.assertIsNone(self.config.replace("path", "value"))

    def test_copy(self):
        self.assertIsNone(self.config.copy("from_path", "path"))

    def test_move(self):
        self.assertIsNone(self.config.move("from_path", "path"))

    def test_test(self):
        self.assertIsNone(self.config.test("path", "value"))

    def test_str(self):
        self.config._operations = []
        self.assertEqual("[]", str(self.config))
