
import shutil
import tempfile
import unittest
from pathlib import PosixPath
from unittest.mock import Mock

from virt_lightning.image_oci_create import OCIImageAssembly


class TestOCIAssemblyImageMake(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"
        self.source_path = PosixPath("tests/oci_data/" + self.image_name)
        self.test_dir = PosixPath(tempfile.mkdtemp())
        self.assembly = OCIImageAssembly(
            self.source_path,
            self.test_dir
        )
        self.image_file = PosixPath(self.image_name + ".tar.gz")

    def test_duplicate_write(self):
        self.assembly.make(self.image_file)
        with self.assertRaises(FileExistsError):
            self.assembly.make(self.image_file)

    def test_empty_output_path(self):
        assembly = OCIImageAssembly(
            self.source_path
        )
        with self.assertRaises(FileNotFoundError):
            assembly.make(self.image_file)

    def test_wrong_output_path(self):
        assembly = OCIImageAssembly(
            self.source_path,
            PosixPath("/tmp/broken/path")
        )
        with self.assertRaises(FileNotFoundError):
            assembly.make(self.image_file)

    def test_validate(self):
        mock_validate_false = Mock(return_value=False)
        self.assembly.validate = mock_validate_false
        with self.assertRaises(ValueError):
            self.assembly.make(self.image_file)

    def tearDown(self):
        shutil.rmtree(self.test_dir)
