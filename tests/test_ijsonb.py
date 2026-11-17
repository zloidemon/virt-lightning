from init_system.jsonb import Jsonb

from virt_lightning.ijsonb import IJsonb


def test_shim():
    assert IJsonb is Jsonb
