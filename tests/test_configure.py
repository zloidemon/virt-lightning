from pathlib import PosixPath
from urllib.parse import urlparse

import virt_lightning.configuration
import virt_lightning.consts


def test_default(monkeypatch):
    with monkeypatch.context() as m:
        config_file = PosixPath(
            virt_lightning.consts.DEFAULT_CONFIGURATION["main"]["ssh_key_file"]
        ).expanduser()

        if not config_file.exists():
            config_file.touch()

        m.setattr(virt_lightning.consts, "DEFAULT_CONFIGFILE", urlparse("a"))
        config = virt_lightning.configuration.ProxyLegacyConfiguration(
            virt_lightning.consts.DEFAULT_CONFIGFILE)
        assert config.root_password == "root"


def test_load_file(monkeypatch, config_file):
    with monkeypatch.context() as m:
        m.setattr(virt_lightning.consts, "DEFAULT_CONFIGFILE", urlparse("a"))
        config = virt_lightning.configuration.ProxyLegacyConfiguration(
            config_file)
        assert config.root_password == "boby"


def test_load_default_config_file(monkeypatch, config_file):
    with monkeypatch.context() as m:
        m.setattr(virt_lightning.consts, "DEFAULT_CONFIGFILE", config_file)
        config = virt_lightning.configuration.ProxyLegacyConfiguration(
            virt_lightning.consts.DEFAULT_CONFIGFILE)
        assert config.root_password == "boby"
