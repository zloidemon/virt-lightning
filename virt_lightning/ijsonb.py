"""
Deprecated: use init_system.jsonb instead.

The IJsonb interface is now the Jsonb protocol of the init_system package.
"""

from virt_lightning.init_system_compat import import_init_system_module

__all__ = ["IJsonb"]  # noqa: F822


def __getattr__(name):
    if name == "IJsonb":
        return import_init_system_module("jsonb").Jsonb
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
