import unittest

from virt_lightning.image_oci_build import OCIImageBuild


class TestOCIBuildImageEnv(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.builder = OCIImageBuild(self.image_name)

    def test_valid_value(self):
        self.builder.env("x", "z")
        self.builder.env("f", "i")
        self.builder.env("r", "1")
        self.builder.env("g", ":")
        valid_values = {
            "x": "z",
            "f": "i",
            "r": "1",
            "g": ":",
        }
        self.assertDictEqual(valid_values, self.builder._OCIImageBuild__env)

    def test_capital_value(self):
        self.builder.env("x", "")
        self.assertDictEqual({"x": ""}, self.builder._OCIImageBuild__env)
        self.builder.env("X", "y")
        self.assertDictEqual({"x": "", "X": "y"}, self.builder._OCIImageBuild__env)

    def test_empty_value(self):
        self.builder.env("x", "")
        self.assertDictEqual({"x": ""}, self.builder._OCIImageBuild__env)

    def test_replace(self):
        self.builder.env("x", "y")
        self.assertDictEqual({"x": "y"}, self.builder._OCIImageBuild__env)
        self.builder.env("x", "y2")
        self.assertDictEqual({"x": "y2"}, self.builder._OCIImageBuild__env)
        self.builder.env("x", "")
        self.assertDictEqual({"x": ""}, self.builder._OCIImageBuild__env)

    def test_wrong_value(self):
        with self.assertRaises(TypeError):
            self.builder.env("x", 1)
        with self.assertRaises(TypeError):
            self.builder.env("x", None)
        with self.assertRaises(TypeError):
            self.builder.env("x", 3.1)
        self.builder.env("x", "3.1")
        self.assertDictEqual({"x": "3.1"}, self.builder._OCIImageBuild__env)

    def test_wrong_key(self):
        with self.assertRaises(TypeError):
            self.builder.env(1, "x")
        with self.assertRaises(TypeError):
            self.builder.env(None, "x")
        with self.assertRaises(TypeError):
            self.builder.env(2.1, "x")
        self.builder.env("f", "none")
        self.assertDictEqual({"f": "none"}, self.builder._OCIImageBuild__env)
