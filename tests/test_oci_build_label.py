import unittest

from virt_lightning.image_oci_build import OCIImageBuild


class TestOCIBuildImageLabels(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.builder = OCIImageBuild(self.image_name)

    def test_valid(self):
        valid_dict = {
            "x": "y",
            "x2": "y2",
            "f": "h",
        }
        self.builder.label("x", "y")
        self.builder.label("x2", "y2")
        self.builder.label("f", "h")

        self.assertIsNotNone(self.builder._OCIImageBuild__labels)
        self.assertDictEqual(valid_dict, self.builder._OCIImageBuild__labels)

    def test_empty_value(self):
        self.builder.label("x", "")
        self.assertDictEqual({"x": ""}, self.builder._OCIImageBuild__labels)

    def test_duplicate(self):
        self.builder.label("x", "y")

        with self.assertRaises(KeyError):
            self.builder.label("x", "y")

    def test_wrong_value(self):
        with self.assertRaises(TypeError):
            self.builder.label("x", 1)
        with self.assertRaises(TypeError):
            self.builder.label("x", None)
        with self.assertRaises(TypeError):
            self.builder.label("x", 3.1)
        self.builder.label("x", "3.1")
        self.assertDictEqual({"x": "3.1"}, self.builder._OCIImageBuild__labels)

    def test_wrong_key(self):
        with self.assertRaises(TypeError):
            self.builder.label(1, "x")
        with self.assertRaises(TypeError):
            self.builder.label(None, "x")
        with self.assertRaises(TypeError):
            self.builder.label(2.1, "x")
        self.builder.label("f", "none")
        self.assertDictEqual({"f": "none"}, self.builder._OCIImageBuild__labels)

    def test_empty_key(self):
        with self.assertRaises(ValueError):
            self.builder.label("", "x")
        self.builder.label("x", "")
        self.assertDictEqual({"x": ""}, self.builder._OCIImageBuild__labels)
