import shutil
import tempfile
import unittest
from pathlib import PosixPath

from virt_lightning.configuration_login_ssh import ConfigurationLoginSSH
from virt_lightning.consts import LoginMethod


class TestConfigurationLoginSSH(unittest.TestCase):
    def setUp(self):
        self.config = ConfigurationLoginSSH()
        self.test_dir = PosixPath(tempfile.mkdtemp())

    def test_method(self):
        self.assertEqual(LoginMethod.SSH, self.config.method)

    def test_method_set(self):
        with self.assertRaises(AttributeError):
            self.config.method = None
        with self.assertRaises(AttributeError):
            self.config.method = "key"
        with self.assertRaises(AttributeError):
            self.config.method = 123

    def test_key_access(self):
        self.assertEqual(None, self.config._ConfigurationLoginSSH__filename)

    def test_key_get_empty(self):
        with self.assertRaises(TypeError):
            self.assertEqual(self.config.key, None)

    def test_key_wrong_type(self):
        with self.assertRaises(TypeError):
            self.config.key = None
        with self.assertRaises(TypeError):
            self.config.key = "file"
        with self.assertRaises(TypeError):
            self.config.key = 1234

    def test_key_not_found(self):
        with self.assertRaises(ValueError):
            self.config.key = PosixPath()

    def test_key_not_file(self):
        with self.assertRaises(ValueError):
            self.config.key = self.test_dir

    def test_key_file(self):
        path_to_key = self.test_dir / PosixPath("test.pub")

        test_file_data = "FIXME: replace it to valid key"

        with path_to_key.open("w") as fh:
            fh.write(test_file_data)

        self.config.key = path_to_key

        self.assertEqual(path_to_key, self.config._ConfigurationLoginSSH__filename)
        self.assertEqual(path_to_key, self.config.key)
        self.assertEqual(self.config.key, self.config._ConfigurationLoginSSH__filename)
        self.assertTrue(self.config.key.is_file())

    def test_key_contains(self):
        path_to_key = self.test_dir / PosixPath("test.pub")

        test_file_data = "FIXME: replace it to valid key"

        with path_to_key.open("w") as fh:
            fh.write(test_file_data)

        self.config.key = path_to_key

        with self.config.key.open("r") as fh:
            data = fh.read()

        self.assertIsNotNone(data)
        self.assertEqual(data, test_file_data)

    def test_eq_method(self):
        path_to_key = self.test_dir / PosixPath("test.pub")

        test_file_data = "FIXME: replace it to valid key"

        with path_to_key.open("w") as fh:
            fh.write(test_file_data)

        test_config_0 = ConfigurationLoginSSH()
        test_config_0.key = path_to_key
        self.config.key = path_to_key
        self.assertEqual(test_config_0, self.config)

    def test_eq_key_invalid(self):
        path_to_key_0 = self.test_dir / PosixPath("test.pub")
        path_to_key_1 = self.test_dir / PosixPath("test2.pub")

        test_file_data = "FIXME: replace it to valid key"

        with path_to_key_0.open("w") as fh:
            fh.write(test_file_data)

        with path_to_key_1.open("w") as fh:
            fh.write(test_file_data)

        test_config_0 = ConfigurationLoginSSH()
        test_config_0.key = path_to_key_0
        self.config.key = path_to_key_1

        self.assertNotEqual(test_config_0, self.config)

    def tearDown(self):
        shutil.rmtree(self.test_dir)
