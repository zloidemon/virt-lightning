"""
Helpers to load the optional init_system package.

The init_system package generates the config drive (cloud-init, Ignition or
OpenStack metadata) of a virtual machine. It is an optional dependency: it is
only needed when a virtual machine is started.
"""

INSTALL_HINT = (
    "The 'init_system' package is required to generate the VM config drive.\n"
    "Install it with:\n"
    "  pip install 'virt-lightning[init]'\n"
    "or, from a local checkout:\n"
    "  pip install -e ../init-system"
)


def import_init_system():
    try:
        import init_system
    except ImportError as e:
        raise ImportError(INSTALL_HINT) from e
    return init_system


def import_init_system_module(name):
    """
    Return the init_system submodule called name.
    """
    return getattr(import_init_system(), name)
