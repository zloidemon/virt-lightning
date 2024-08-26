import json
import unittest
import shutil
import json
import tempfile
import tarfile

from pathlib import PosixPath
from virt_lightning.image_oci_index import OCIIndex
from virt_lightning.image_oci_manifest import OCIManifest
from virt_lightning.image_oci_layout import OCIImageLayout


class TestOCITarImage(unittest.TestCase):
    def setUp(self):
        self.image_name = "test"

        with PosixPath(f"tests/oci_data/{self.image_name}/index.json").open() as fh:
            self.index = OCIIndex(json.loads(fh.read()))

        with PosixPath(f"tests/oci_data/{self.image_name}/manifest.json").open() as fh:
            self.manifest = OCIManifest(json.loads(fh.read()))

        self.test_dir = PosixPath(tempfile.mkdtemp())
        self.image_path = self.test_dir / self.image_name

        self.image_path.mkdir(parents=True, exist_ok=True)

        for _top in ["oci-layout", "index.json"]:
            shutil.copyfile(
                f"tests/oci_data/{self.image_name}/{_top}",
                self.image_path / _top
            )

        manifest = self.index.manifests[0]

        algo, hsum = manifest.digest

        blobs = self.image_path / "blobs" / algo
        blobs.mkdir(parents=True, exist_ok=True)

        shutil.copyfile(f"tests/oci_data/{self.image_name}/manifest.json", blobs / hsum)

        algo, hsum = self.manifest.config.digest

        shutil.copyfile(f"tests/oci_data/{self.image_name}/config.json", blobs / hsum)

        with tarfile.open(f"{self.image_path}.tar.gz", mode="w:gz") as tar:
            tar.add(self.image_path, "/")

    def test_tar_read(self):
        archive = PosixPath(str(self.image_path) + ".tar.gz")

        self.assertTrue(archive.is_file())
        self.assertTrue(tarfile.is_tarfile(archive))

        tar = tarfile.open(archive, mode="r")

        tar_layout = OCIImageLayout(json.loads(tar.extractfile("oci-layout").read()))
        tar_index = OCIIndex(json.loads(tar.extractfile("index.json").read()))


        self.assertEqual(tar_layout.version, "1.0.0")
        self.assertEqual(tar_index.schema_version, self.index.schema_version)
        self.assertEqual(len(tar_index.manifests), len(self.index.manifests))

    def tearDown(self):
        shutil.rmtree(self.test_dir)
