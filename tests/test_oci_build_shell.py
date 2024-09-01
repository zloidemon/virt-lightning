import unittest
from pathlib import PosixPath

from virt_lightning.image_oci_build import OCIImageBuild


class TestOCIBuildImageShell(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.builder = OCIImageBuild(self.image_name)

    def test_shell_valid(self):
        filename = PosixPath("csh")

        self.assertEqual(None, self.builder._OCIImageBuild__shell)
        self.builder.shell(filename)

        self.assertEqual(filename, self.builder._OCIImageBuild__shell)

    def test_shell_wrong(self):
        with self.assertRaises(TypeError):
            self.builder.shell(None)
        with self.assertRaises(TypeError):
            self.builder.shell(1234)
        with self.assertRaises(TypeError):
            self.builder.shell("wrong")
        with self.assertRaises(TypeError):
            self.builder.shell("wrong", "--f")

        self.assertEqual(None, self.builder._OCIImageBuild__shell)

    def test_args_empty(self):
        self.assertListEqual([], self.builder._OCIImageBuild__shell_args)

    def test_args_valid(self):
        filename = PosixPath("csh")
        args = ["--test", "args", "-f", "none"]

        self.assertListEqual([], self.builder._OCIImageBuild__shell_args)

        self.builder.shell(filename, *args)

        self.assertListEqual(args, self.builder._OCIImageBuild__shell_args)

    def test_args_valid_spaces(self):
        filename = PosixPath("csh")
        args = ["--test", "", "-f", ""]

        self.assertListEqual([], self.builder._OCIImageBuild__shell_args)

        self.builder.shell(filename, *args)

        self.assertListEqual(["--test", "-f"], self.builder._OCIImageBuild__shell_args)

    def test_args_wrong_types(self):
        filename = PosixPath("csh")

        with self.assertRaises(TypeError):
            self.builder.shell(filename, None)
        with self.assertRaises(TypeError):
            self.builder.shell(filename, 1)
        with self.assertRaises(TypeError):
            self.builder.shell(filename, "3", None)
        with self.assertRaises(TypeError):
            self.builder.shell(filename, "3", 1, "123")
        with self.assertRaises(TypeError):
            self.builder.shell(filename, [])
        with self.assertRaises(TypeError):
            self.builder.shell(filename, ())
