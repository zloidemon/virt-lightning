import unittest

from virt_lightning.configuration_posix_user import ConfigurationPosixUser
from virt_lightning.image_oci_build import OCIImageBuild


class TestOCIBuildImageUser(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.builder = OCIImageBuild(self.image_name)

    def test_valid(self):
        user = ConfigurationPosixUser()

        user.username = "user_test"
        user.groupname = "group_test"
        user.password = "password"
        user.uid = 123
        user.gid = 123

        self.assertIsNone(self.builder._OCIImageBuild__user)

        self.builder.user(user)

        self.assertEqual(user, self.builder._OCIImageBuild__user)

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            self.builder.user("username")
        with self.assertRaises(TypeError):
            self.builder.user(None)
        with self.assertRaises(TypeError):
            self.builder.user(1234)
