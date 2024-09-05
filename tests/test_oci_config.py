import json
import unittest
from datetime import datetime
from pathlib import PosixPath

from virt_lightning.consts import SignalShutdown
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

    def test_required_rootfs(self):
        self.assertIsNotNone(self.config_req.rootfs)
        self.assertEqual(self.config_req.rootfs.type, "layers")
        valid = [
            ("sha256", "c6f988f4874bb0add23a778f753c65efe992244e148a1d2ec2a8b664fb66bbd1"),
            ("sha256", "5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef"),
        ]
        self.assertListEqual(self.config_req.rootfs.diff_ids, valid)

    def test_roots_str(self):
        self.assertEqual("Config(type=layers,diff_ids=2)", str(self.config_req.rootfs))

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

    def test_optional_config_user(self):
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

    def test_optional_config_cmd(self):
        self.assertListEqual(
            ["--foreground", "--config", "/etc/my-app.d/default.cfg"],
            self.config_opt.config.cmd
        )

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

    def test_optional_rootfs(self):
        self.assertIsNotNone(self.config_opt.rootfs)
        self.assertEqual(self.config_opt.rootfs.type, "layers")
        valid = [
            ("sha256", "c6f988f4874bb0add23a778f753c65efe992244e148a1d2ec2a8b664fb66bbd1"),
            ("sha256", "5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef"),
        ]
        self.assertListEqual(self.config_opt.rootfs.diff_ids, valid)

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

    def test_str(self):
        self.assertEqual(
            "Config(architecture=amd64,os=linux)",
            str(self.config_req)
        )


#
# FIXME: Дополняет старый тест, кторый берет данный из файла, хотя надо разбить
#        на много отдельных тестов, по каждому из полей в объекте.
#
class TestOCIConfigExtended(unittest.TestCase):
    def setUp(self):
        with PosixPath("tests/oci_data/config_from_spec.json").open() as fh:
            self.config_opt = OCIConfig(json.loads(fh.read()))

    def test_optional_config_volumes_none(self):
        self.config_opt.config._OCIConfigConfig__data["Volumes"] = None
        self.assertIsNone(self.config_opt.config.volumes)

        del(self.config_opt.config._OCIConfigConfig__data["Volumes"])
        self.assertIsNone(self.config_opt.config.volumes)

    def test_optional_config_memory(self):
        self.config_opt.config._OCIConfigConfig__data["Memory"] = 1
        self.assertGreater(self.config_opt.config.memory, 0)

    def test_optional_config_memory_wrong(self):
        self.config_opt.config._OCIConfigConfig__data["Memory"] = -1
        with self.assertRaises(ValueError):
            self.assertGreater(self.config_opt.config.memory, 0)
        self.config_opt.config._OCIConfigConfig__data["Memory"] = 0
        with self.assertRaises(ValueError):
            self.assertGreater(self.config_opt.config.memory, 0)

    def test_optional_config_memory_none(self):
        self.assertIsNone(self.config_opt.config.memory)

    def test_optional_config_memory_swap(self):
        self.config_opt.config._OCIConfigConfig__data["MemorySwap"] = 1
        self.assertGreater(self.config_opt.config.memory_swap, 0)

    def test_optional_config_memory_swap_wrong(self):
        self.config_opt.config._OCIConfigConfig__data["MemorySwap"] = -1
        with self.assertRaises(ValueError):
            self.assertGreater(self.config_opt.config.memory_swap, 0)
        self.config_opt.config._OCIConfigConfig__data["MemorySwap"] = 0
        with self.assertRaises(ValueError):
            self.assertGreater(self.config_opt.config.memory_swap, 0)

    def test_optional_config_memory_swap_none(self):
        self.assertIsNone(self.config_opt.config.memory_swap)

    def test_optional_config_cpu_shares(self):
        self.config_opt.config._OCIConfigConfig__data["CpuShares"] = 1
        self.assertGreater(self.config_opt.config.cpu_shares, 0)

    def test_optional_config_cpu_shares_wrong(self):
        self.config_opt.config._OCIConfigConfig__data["CpuShares"] = -1
        with self.assertRaises(ValueError):
            self.assertGreater(self.config_opt.config.cpu_shares, 0)
        self.config_opt.config._OCIConfigConfig__data["CpuShares"] = 0
        with self.assertRaises(ValueError):
            self.assertGreater(self.config_opt.config.cpu_shares, 0)

    def test_optional_config_cpu_shares_none(self):
        self.assertIsNone(self.config_opt.config.cpu_shares)

    def test_optional_config_entrypoint_none(self):
        self.config_opt.config._OCIConfigConfig__data["Entrypoint"] = None
        self.assertIsNone(self.config_opt.config.entrypoint)

        del(self.config_opt.config._OCIConfigConfig__data["Entrypoint"])
        self.assertIsNone(self.config_opt.config.entrypoint)

    def test_optional_config_user_none(self):
        self.config_opt.config._OCIConfigConfig__data["User"] = None
        self.assertIsNone(self.config_opt.config.user)

        del(self.config_opt.config._OCIConfigConfig__data["User"])
        self.assertIsNone(self.config_opt.config.user)

    def test_optional_config_ports_none(self):
        self.config_opt.config._OCIConfigConfig__data["ExposedPorts"] = None
        self.assertIsNone(self.config_opt.config.exposed_ports)

        del(self.config_opt.config._OCIConfigConfig__data["ExposedPorts"])
        self.assertIsNone(self.config_opt.config.exposed_ports)

    def test_optional_config_env_none(self):
        self.config_opt.config._OCIConfigConfig__data["Env"] = None
        self.assertIsNone(self.config_opt.config.env)

        del(self.config_opt.config._OCIConfigConfig__data["Env"])
        self.assertIsNone(self.config_opt.config.env)

    def test_optional_config_labels_none(self):
        self.config_opt.config._OCIConfigConfig__data["Labels"] = None
        self.assertDictEqual({}, self.config_opt.config.labels)

        del(self.config_opt.config._OCIConfigConfig__data["Labels"])
        self.assertDictEqual({}, self.config_opt.config.labels)

    def test_optional_config_cmd_none(self):
        self.config_opt.config._OCIConfigConfig__data["Cmd"] = None
        self.assertListEqual([], self.config_opt.config.cmd)

        del(self.config_opt.config._OCIConfigConfig__data["Cmd"])
        self.assertEqual([], self.config_opt.config.cmd)

    #
    # FIXME: В OCI документации написано что в резевре, но описания как будет
    #        ничего нет. Пока для теста оставим строчный true, далее надо будет
    #        заменить уже на существующий Healthcheck
    #
    def test_optional_config_healthcheck_str(self):
        self.config_opt.config._OCIConfigConfig__data["Healthcheck"] = "true"
        self.assertEqual("true", self.config_opt.config.healthcheck)

    def test_optional_config_healthcheck_none(self):
        self.assertIsNone(self.config_opt.config.healthcheck)

    def test_optional_config_stop_signal_none(self):
        self.assertIsNone(self.config_opt.config.stop_signal)

    def test_optional_config_stop_signal_acpi(self):
        self.config_opt.config._OCIConfigConfig__data["StopSignal"] = SignalShutdown.ACPI
        self.assertEqual(SignalShutdown.ACPI, self.config_opt.config.stop_signal)

    def test_optional_config_workingdir_none(self):
        self.config_opt.config._OCIConfigConfig__data["WorkingDir"] = None
        self.assertIsNone(self.config_opt.config.workingdir)

        del(self.config_opt.config._OCIConfigConfig__data["WorkingDir"])
        self.assertIsNone(self.config_opt.config.workingdir)


    def test_optional_history_author(self):
        self.assertIsNone(self.config_opt.history[0].author)
        self.assertIsNone(self.config_opt.history[1].author)
        self.assertIsNone(self.config_opt.history[2].author)

    def test_optional_history_comment(self):
        self.assertIsNone(self.config_opt.history[0].comment)
        self.assertIsNone(self.config_opt.history[1].comment)
        self.assertIsNone(self.config_opt.history[2].comment)

    def test_optional_history_created(self):
        self.assertIsNotNone(self.config_opt.history[0].created)
        self.assertIsNotNone(self.config_opt.history[1].created)
        self.assertIsNotNone(self.config_opt.history[2].created)
        self.assertEqual(
            datetime.fromisoformat("2015-10-31T22:22:54.690851953Z"),
            self.config_opt.history[0].created
        )
        self.assertEqual(
            datetime.fromisoformat("2015-10-31T22:22:55.613815829Z"),
            self.config_opt.history[1].created
        )
        self.assertEqual(
            datetime.fromisoformat("2015-10-31T22:22:56.329850019Z"),
            self.config_opt.history[2].created
        )

    def test_optional_history_created_none(self):
        self.config_opt.history[0]._OCIHistoryRecord__data["created"] = None
        self.assertIsNone(self.config_opt.history[0].created)

        del(self.config_opt.history[0]._OCIHistoryRecord__data["created"])
        self.assertIsNone(self.config_opt.history[0].created)

        self.config_opt.history[1]._OCIHistoryRecord__data["created"] = None
        self.assertIsNone(self.config_opt.history[1].created)

        del(self.config_opt.history[1]._OCIHistoryRecord__data["created"])
        self.assertIsNone(self.config_opt.history[1].created)

        self.config_opt.history[2]._OCIHistoryRecord__data["created"] = None
        self.assertIsNone(self.config_opt.history[2].created)

        del(self.config_opt.history[2]._OCIHistoryRecord__data["created"])
        self.assertIsNone(self.config_opt.history[2].created)

    def test_history_str(self):
        self.assertEqual(
            "Record(created_by=96,empty_layer=False)",
            str(self.config_opt.history[0])
        )
        self.assertEqual(
            "Record(created_by=28,empty_layer=True)",
            str(self.config_opt.history[1])
        )
        self.assertEqual(
            "Record(created_by=23,empty_layer=False)",
            str(self.config_opt.history[2])
        )

    def test_str(self):
        self.assertEqual(
            "Config(architecture=amd64,os=linux)",
            str(self.config_opt)
        )
