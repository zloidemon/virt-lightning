"""
Deprecated: use init_system.execfile_mkpasswd instead.
"""

from virt_lightning.init_system_compat import import_init_system_module

__all__ = ["ExecFileMkpasswd"]  # noqa: F822


def __getattr__(name):
    if name in __all__:
        return getattr(import_init_system_module("execfile_mkpasswd"), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
