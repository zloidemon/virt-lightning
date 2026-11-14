import unittest
from pathlib import PosixPath

from virt_lightning.consts import HashingAlgorithm
from virt_lightning.image_oci_create import OCIImageAssembly


class TestOCIAssemblyImageLoadFile(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.source_path = PosixPath("tests/oci_data/" + self.image_name)
        self.assembly = OCIImageAssembly(self.source_path)

    def test_load_file(self):
        index_file = self.source_path / "index.json"
        hsum, data = self.assembly._OCIImageAssembly__load_file(index_file, None)
        self.assertIsNone(hsum)
        self.assertIsNotNone(data)

        hsum, data = self.assembly._OCIImageAssembly__load_file(
            index_file, HashingAlgorithm.SHA256
        )
        self.assertEqual(
            hsum, "d178553175a5e39c728fc2a215545b8dff875b6d68c21b992712a0e2023872f8"
        )

        hsum, data = self.assembly._OCIImageAssembly__load_file(
            index_file, HashingAlgorithm.SHA512
        )
        self.assertEqual(
            hsum,
            "966588d92cbed62c12a83742d6362b7e8c7a884e5b69d6125034bcb54678d24a"
            "3ecc2afe4ab0f712ababe82612d99c99c71613748807d731a227838eeb46f9bf",
        )
