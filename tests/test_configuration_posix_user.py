import unittest

from virt_lightning.configuration_posix_user import ConfigurationPosixUser


class TestConfigurationPosixUser(unittest.TestCase):
    def setUp(self):
        self.config = ConfigurationPosixUser()

    def test_uid_valid(self):
        self.config.uid = 0
        self.assertEqual(self.config.uid, self.config._ConfigurationPosixUser__uid)

        self.config.uid = 1
        self.assertEqual(self.config.uid, self.config._ConfigurationPosixUser__uid)

        self.config.uid = 65535
        self.assertEqual(self.config.uid, self.config._ConfigurationPosixUser__uid)

    def test_uid_empty(self):
        self.assertEqual(None, self.config._ConfigurationPosixUser__uid)
        with self.assertRaises(AttributeError):
            self.assertEqual(self.config.uid, None)

    def test_uid_wrong_type(self):
        with self.assertRaises(TypeError):
            self.config.uid = None
        with self.assertRaises(TypeError):
            self.config.uid = "1234"
        with self.assertRaises(TypeError):
            self.config.uid = 1.0

    def test_uid_wrong_negative(self):
        with self.assertRaises(ValueError):
            self.config.uid = -1
        with self.assertRaises(ValueError):
            self.config.uid = -500

    #
    # NOTE: gid тесты на самом деле такие же как и для uid
    #
    def test_gid_valid(self):
        self.config.gid = 0
        self.assertEqual(self.config.gid, self.config._ConfigurationPosixUser__gid)

        self.config.gid = 1
        self.assertEqual(self.config.gid, self.config._ConfigurationPosixUser__gid)

        self.config.gid = 65535
        self.assertEqual(self.config.gid, self.config._ConfigurationPosixUser__gid)

    def test_gid_empty(self):
        self.assertEqual(None, self.config._ConfigurationPosixUser__gid)
        with self.assertRaises(AttributeError):
            self.assertEqual(self.config.gid, None)

    def test_gid_wrong_type(self):
        with self.assertRaises(TypeError):
            self.config.gid = None
        with self.assertRaises(TypeError):
            self.config.gid = "1234"
        with self.assertRaises(TypeError):
            self.config.gid = 1.0

    def test_gid_wrong_negative(self):
        with self.assertRaises(ValueError):
            self.config.gid = -1
        with self.assertRaises(ValueError):
            self.config.gid = -500

    def test_username_valid(self):
        self.config.username = "hello"
        self.assertEqual(
            self.config.username, self.config._ConfigurationPosixUser__username
        )

    def test_username_get_empty(self):
        with self.assertRaises(AttributeError):
            self.assertEqual(self.config.username, None)

    def test_username_set_empty(self):
        with self.assertRaises(ValueError):
            self.config.username = ""

    def test_username_wrong_type(self):
        with self.assertRaises(TypeError):
            self.config.username = None
        with self.assertRaises(TypeError):
            self.config.username = 1234
        with self.assertRaises(TypeError):
            self.config.username = 1.0

    #
    # FIXME: groupname тесты на самом деле такие же как и для username, но могут
    #        быть иными после добавления проверок передаваемых символов
    #
    def test_groupname_valid(self):
        self.config.groupname = "hello"
        self.assertEqual(
            self.config.groupname, self.config._ConfigurationPosixUser__groupname
        )

    def test_groupname_get_empty(self):
        with self.assertRaises(AttributeError):
            self.assertEqual(self.config.groupname, None)

    def test_groupname_set_empty(self):
        with self.assertRaises(ValueError):
            self.config.groupname = ""

    def test_groupname_wrong_type(self):
        with self.assertRaises(TypeError):
            self.config.groupname = None
        with self.assertRaises(TypeError):
            self.config.groupname = 1234
        with self.assertRaises(TypeError):
            self.config.groupname = 1.0

    #
    # FIXME: password тесты на самом деле такие же как и для username, но могут
    #        быть иными после добавления проверок передаваемых символов
    #
    def test_password_valid(self):
        self.config.password = "password"
        self.assertEqual(
            self.config.password, self.config._ConfigurationPosixUser__password
        )

    def test_password_get_empty(self):
        with self.assertRaises(AttributeError):
            self.assertEqual(self.config.password, None)

    def test_password_set_empty(self):
        with self.assertRaises(ValueError):
            self.config.password = ""

    def test_password_wrong_type(self):
        with self.assertRaises(TypeError):
            self.config.password = None
        with self.assertRaises(TypeError):
            self.config.password = 1234
        with self.assertRaises(TypeError):
            self.config.password = 1.0

    def test_login(self):
        self.assertIsNone(self.config.login)
        self.config.login = True
        self.assertTrue(self.config.login)


class TestConfigurationPosixUserEqual(unittest.TestCase):
    def setUp(self):
        self.config = ConfigurationPosixUser()

    def test_eq_wrong_username(self):
        config = ConfigurationPosixUser()

        self.config.username = "hello"
        config.username = "olleh"

        self.assertNotEqual(self.config, config)

    def test_eq_worng_username_excp(self):
        config = ConfigurationPosixUser()

        self.assertNotEqual(self.config, config)

    def test_eq_wrong_groupname(self):
        config = ConfigurationPosixUser()

        self.config.username = "hello"
        self.config.groupname = "hello"

        config.username = "hello"
        config.groupname = "olleh"

        self.assertNotEqual(self.config, config)

    def test_eq_worng_groupname_excp(self):
        config = ConfigurationPosixUser()

        self.config.username = "hello"
        self.config.groupname = "hello"

        config.username = "hello"

        self.assertNotEqual(self.config, config)

    def test_eq_wrong_uid(self):
        config = ConfigurationPosixUser()

        self.config.username = "hello"
        self.config.groupname = "hello"
        self.config.uid = 100

        config.username = "hello"
        config.groupname = "hello"
        config.uid = 1000

        self.assertNotEqual(self.config, config)

    def test_eq_worng_uid_excp(self):
        config = ConfigurationPosixUser()

        self.config.username = "hello"
        self.config.groupname = "hello"
        self.config.uid = 100

        config.username = "hello"
        config.groupname = "hello"

        self.assertNotEqual(self.config, config)

    def test_eq_wrong_gid(self):
        config = ConfigurationPosixUser()

        self.config.username = "hello"
        self.config.groupname = "hello"
        self.config.uid = 100
        self.config.gid = 100

        config.username = "hello"
        config.groupname = "hello"
        config.uid = 100
        config.gid = 1000

        self.assertNotEqual(self.config, config)

    def test_eq_worng_gid_excp(self):
        config = ConfigurationPosixUser()

        self.config.username = "hello"
        self.config.groupname = "hello"
        self.config.uid = 100
        self.config.gid = 100

        config.username = "hello"
        config.groupname = "hello"
        config.uid = 100

        self.assertNotEqual(self.config, config)

    def test_eq_wrong_password(self):
        config = ConfigurationPosixUser()

        self.config.username = "hello"
        self.config.groupname = "hello"
        self.config.uid = 100
        self.config.gid = 100
        self.config.password = "password"

        config.username = "hello"
        config.groupname = "hello"
        config.uid = 100
        config.gid = 100
        config.password = "drowssap"

        self.assertNotEqual(self.config, config)

    def test_eq_worng_password_excp(self):
        config = ConfigurationPosixUser()

        self.config.username = "hello"
        self.config.groupname = "hello"
        self.config.uid = 100
        self.config.gid = 100
        self.config.password = "password"

        config.username = "hello"
        config.groupname = "hello"
        config.uid = 100
        config.gid = 100

        self.assertNotEqual(self.config, config)
