import json
import unittest
import urllib.error
from types import SimpleNamespace
from unittest.mock import patch

from virt_lightning.downloader_native import DownloaderNative
from virt_lightning.idownloader import IDownloader


class FakeHTTPResponse:
    def __init__(self, content, headers=None):
        self.content = content
        self.headers = headers or {}
        self.consumed = False

    def read(self, size=-1):
        if self.consumed:
            return b""
        self.consumed = True
        return self.content


class TestIDownloader(unittest.TestCase):
    @patch.multiple(IDownloader, __abstractmethods__=set())
    def setUp(self):
        self.downloader = IDownloader("configuration", "storage_dir")

    def test_pull(self):
        self.assertIsNone(self.downloader.pull())


def test_pull_skips_json_on_404(tmp_path):
    (tmp_path / "upstream").mkdir()
    image_content = b"qcow2"
    image_response = FakeHTTPResponse(
        image_content,
        {"Last-Modified": "now", "Content-Length": str(len(image_content))},
    )

    def fake_urlopen(url):
        if url.endswith(".json"):
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
        return image_response

    configuration = SimpleNamespace(
        registry_urls=[SimpleNamespace(entrypoint="http://example.com/{resource}/{hashsum}")]
    )
    downloader = DownloaderNative(configuration, tmp_path)
    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        downloader.pull(image="ubuntu:20.04")

    assert (tmp_path / "upstream" / "ubuntu-20.04.qcow2").read_bytes() == image_content
    assert not (tmp_path / "upstream" / "ubuntu-20.04.json").exists()


def test_pull_writes_json(tmp_path):
    (tmp_path / "upstream").mkdir()
    image_content = b"qcow2"
    metadata = b'{"memory": 1024}'
    image_response = FakeHTTPResponse(
        image_content,
        {"Last-Modified": "now", "Content-Length": str(len(image_content))},
    )

    def fake_urlopen(url):
        if url.endswith(".json"):
            return FakeHTTPResponse(metadata)
        return image_response

    configuration = SimpleNamespace(
        registry_urls=[SimpleNamespace(entrypoint="http://example.com/{resource}/{hashsum}")]
    )
    downloader = DownloaderNative(configuration, tmp_path)
    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        downloader.pull(image="ubuntu:20.04")

    assert json.loads((tmp_path / "upstream" / "ubuntu-20.04.json").read_text()) == {
        "memory": 1024
    }
