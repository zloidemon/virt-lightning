import json
import unittest
from pathlib import PosixPath

from virt_lightning.image_oci_config import OCIConfig


class TestOCIConfig(unittest.TestCase):
    def setUp(self):
        with PosixPath("tests/oci_data/config_from_spec.json").open() as fh:
            self.config_opt = OCIConfig(json.loads(fh.read()))
        with PosixPath("tests/oci_data/config_req.json").open() as fh:
            self.config_req = OCIConfig(json.loads(fh.read()))

    def test_required_created(self):
        self.assertIsNone(self.config_req.created)

    def test_required_author(self):
        self.assertIsNone(self.config_req.author)

    def test_required_architecture(self):
        self.assertIsNotNone(self.config_req.architecture)
        self.assertEqual(self.config_req.architecture, "amd64")

    def test_required_os(self):
        self.assertIsNotNone(self.config_req.os)
        self.assertEqual(self.config_req.os, "linux")

    def test_required_os_version(self):
        self.assertIsNone(self.config_req.os_version)

    def test_required_os_features(self):
        self.assertIsNotNone(self.config_req.os_features)
        self.assertEqual(len(self.config_req.os_features), 0)
        self.assertListEqual(self.config_req.os_features, [])

    def test_required_variant(self):
        self.assertIsNone(self.config_req.variant)

    def test_required_history(self):
        self.assertIsNotNone(self.config_req.history)
        self.assertEqual(len(self.config_req.history), 0)
        self.assertListEqual(self.config_req.history, [])

    def test_required_config(self):
        self.assertIsNone(self.config_req.config)

    # NOTE: Опциональные поля из примера объекта в спецификации

    def test_optional_created(self):
        self.assertIsNotNone(self.config_opt.created)

    def test_optional_author(self):
        self.assertIsNotNone(self.config_opt.author)

    def test_optional_architecture(self):
        self.assertIsNotNone(self.config_opt.architecture)
        self.assertEqual(self.config_opt.architecture, "amd64")

    def test_optional_os(self):
        self.assertIsNotNone(self.config_opt.os)
        self.assertEqual(self.config_opt.os, "linux")

    def test_optional_os_version(self):
        self.assertIsNone(self.config_opt.os_version)

    def test_optional_os_features(self):
        self.assertIsNotNone(self.config_opt.os_features)
        self.assertEqual(len(self.config_opt.os_features), 0)
        self.assertListEqual(self.config_opt.os_features, [])

    def test_optional_variant(self):
        self.assertIsNone(self.config_opt.variant)

    def test_optional_history_simple(self):
        self.assertIsNotNone(self.config_opt.history)
        self.assertEqual(len(self.config_opt.history), 3)
        self.assertGreater(len(self.config_opt.history), 0)

    def test_optional_config(self):
        self.assertIsNotNone(self.config_opt.config)
        self.assertEqual(self.config_opt.config.user, "alice")

    def test_optional_config_ports(self):
        self.assertDictEqual(self.config_opt.config.exposed_ports, {"8080/tcp": {}})

    def test_optional_config_env(self):
        valid = {
            "BAR": "well_written_spec",
            "FOO": "oci_is_a",
            "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        }
        self.assertDictEqual(self.config_opt.config.env, valid)

    def test_optional_config_entrypoint(self):
        self.assertListEqual(self.config_opt.config.entrypoint, ["/bin/my-app-binary"])

    def test_optional_config_volumes(self):
        valid = {"/var/job-result-data": {}, "/var/log/my-app-logs": {}}
        self.assertDictEqual(self.config_opt.config.volumes, valid)

    def test_optional_config_workingdir(self):
        self.assertEqual(self.config_opt.config.workingdir, "/home/alice")

    def test_optional_config_labels(self):
        valid = {
            "com.example.project.git.commit": "45a939b2999782a3f005621a8d0f29aa387e1d6b",
            "com.example.project.git.url": "https://example.com/project.git",
        }
        self.assertDictEqual(self.config_opt.config.labels, valid)

    #
    # FIXME: Добавить поддержку проверку даты создания через datetime
    #
    def test_optional_history(self):
        self.assertIsNotNone(self.config_opt.history)
        valid_0 = (
            "/bin/sh -c #(nop) ADD "
            "file:a3bc1e842b69636f9df5256c49c5374fb4eef1e281fe3f282c65fb853ee171c5 in /"
        )
        self.assertFalse(self.config_opt.history[0].empty_layer)
        self.assertEqual(self.config_opt.history[0].created_by, valid_0)
        valid_1 = '/bin/sh -c #(nop) CMD ["sh"]'
        self.assertTrue(self.config_opt.history[1].empty_layer)
        self.assertEqual(self.config_opt.history[1].created_by, valid_1)
        valid_2 = "/bin/sh -c apk add curl"
        self.assertFalse(self.config_opt.history[2].empty_layer)
        self.assertEqual(self.config_opt.history[2].created_by, valid_2)
