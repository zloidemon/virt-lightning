import unittest
from unittest.mock import patch

from virt_lightning.idownloader import IDownloader


class TestIDownloader(unittest.TestCase):
    @patch.multiple(IDownloader, __abstractmethods__=set())
    def setUp(self):
        self.downloader = IDownloader("configuration", "storage_dir")

    def test_pull(self):
        self.assertIsNone(self.downloader.pull())
