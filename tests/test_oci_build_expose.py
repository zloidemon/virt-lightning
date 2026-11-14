import unittest

from virt_lightning.image_oci_build import OCIImageBuild


class TestOCIBuildImageExpose(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.builder = OCIImageBuild(self.image_name)

    def test_empty_protocol(self):
        self.builder.expose(5000)
        self.assertSetEqual(set({"5000/tcp"}), self.builder._OCIImageBuild__ports)

    def test_duplicate_protocol(self):
        self.builder.expose(5000)

        with self.assertRaises(KeyError):
            self.builder.expose(5000)

        with self.assertRaises(KeyError):
            self.builder.expose(5000, "tcp")

        self.builder.expose(5000, "udp")

        with self.assertRaises(KeyError):
            self.builder.expose(5000, "udp")

    def test_tcp_and_udp_port(self):
        self.builder.expose(5000, "tcp")
        self.builder.expose(5000, "udp")

        self.assertSetEqual(
            set({"5000/tcp", "5000/udp"}), self.builder._OCIImageBuild__ports
        )

    def test_valid_udp(self):
        self.builder.expose(5000, "udp")
        self.assertSetEqual(set({"5000/udp"}), self.builder._OCIImageBuild__ports)

    def test_valid_tcp(self):
        self.builder.expose(5000, "udp")
        self.assertSetEqual(set({"5000/udp"}), self.builder._OCIImageBuild__ports)

    def test_invalid_protocol(self):
        with self.assertRaises(ValueError):
            self.builder.expose(5000, "n")
        with self.assertRaises(ValueError):
            self.builder.expose(5000, None)
        with self.assertRaises(ValueError):
            self.builder.expose(5000, 123)

    def test_invalid_port_type(self):
        with self.assertRaises(TypeError):
            self.builder.expose("5000")
        with self.assertRaises(TypeError):
            self.builder.expose(5000.0)
        with self.assertRaises(TypeError):
            self.builder.expose(None)

    def test_invalid_range(self):
        with self.assertRaises(ValueError):
            self.builder.expose(-1)
        with self.assertRaises(ValueError):
            self.builder.expose(65536)

    def test_valid_range(self):
        self.builder.expose(0)
        self.builder.expose(65535)
        self.assertSetEqual(
            set({"0/tcp", "65535/tcp"}), self.builder._OCIImageBuild__ports
        )
