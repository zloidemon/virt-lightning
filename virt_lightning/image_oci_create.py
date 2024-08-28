import hashlib
import json
import tarfile
from pathlib import PosixPath

from virt_lightning.image_oci_config import OCIConfigConfig
from virt_lightning.image_oci_index import OCIIndex
from virt_lightning.image_oci_manifest import OCIManifest
from virt_lightning.image_oci_media_type import ImageEnumEntry


class OCIImageAssembly:
    def __init__(self, src, dst=None):
        self.__src = src
        self.__dst = dst
        self.__index_file = None

    def __calc_checksum(self, data, algo):
        encoded_data = data.encode()

        match algo:
            case "sha256":
                hsum = hashlib.sha256(encoded_data)
            case "sha512":
                hsum = hashlib.sha512(encoded_data)
            case _:
                raise NotImplementedError(algo)
        return hsum.hexdigest()

    def __load_file(self, filename, algo=None):
        data = None
        hsum = None

        with PosixPath(filename).open() as fh:
            data = fh.read()

        if algo:
            hsum = self.__calc_checksum(data, algo)

        return (hsum, data)

    @property
    def __index(self):
        if not self.__index_file:
            _, _data = self.__load_file(self.__src / "index.json")
            self.__index_file = OCIIndex(json.loads(_data))
        return self.__index_file

    def __validate_config(self, configfile):
        if not configfile.media_type.is_oci():
            return False

        if configfile.media_type.entry == ImageEnumEntry.config:
            _config_algo, hsum = configfile.digest
            _config_blob = self.__src / "blobs" / _config_algo / hsum

            if not _config_blob.exists() or not _config_blob.is_file():
                return False

            if _config_blob.stat().st_size != configfile.size:
                return False

            _hsum, _config_data = self.__load_file(_config_blob, _config_algo)

            if _hsum != hsum:
                return False

            OCIConfigConfig(json.loads(_config_data))
            return True
        return False

    def __validate_manifest(self, manifest):
        algo, hsum = manifest.digest
        blob = self.__src / "blobs" / algo / hsum

        if not manifest.media_type.is_oci():
            return False

        if manifest.media_type.entry != ImageEnumEntry.manifest:
            return False

        if not blob.exists() or not blob.is_file():
            return False

        if blob.stat().st_size != manifest.size:
            return False

        _hsum, data = self.__load_file(blob, algo)

        if hsum != _hsum:
            return False

        _manifest = OCIManifest(json.loads(data))

        return self.__validate_config(_manifest.config)

    def validate(self):
        if not self.__index.media_type.is_oci():
            return False

        if self.__index.media_type.entry != ImageEnumEntry.index:
            return False

        if len(self.__index.manifests) < 1:
            return False

        return all(
            self.__validate_manifest(manifest) for manifest in self.__index.manifests
        )

    def inspect(self):
        return self.__index

    def make(self, filename):
        if not self.__dst:
            raise FileNotFoundError("export location not defined")

        if not self.__dst.exists():
            raise FileNotFoundError("not found location")

        if not self.validate():
            raise ValueError("invalid data to pack")

        image = self.__dst / filename

        if image.is_file():
            raise FileExistsError("image already exists")

        with tarfile.open(image, mode="w:gz") as tar:
            tar.add(self.__src, "/")
