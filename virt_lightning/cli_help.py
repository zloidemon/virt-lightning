import grp
import os
import sys

from virt_lightning.consts import DEFAULT_LIBVIRT_GROUP

_HELP_MESSAGE = """
Cannot access to VMM service. Your user should probably be in the "{groupname}"
group. You can add the user "{username}" in the group "{groupname}" with the
following command:

    sudo usermod --append --groups libvirt {username}
"""


class CLIHelp:
    def __init__(self, action_subparsers, parent_parser):
        pass

    @staticmethod
    def run():
        import getpass

        def get_local_libvirt_group():
            for entry in grp.getgrall():
                if entry.gr_name == DEFAULT_LIBVIRT_GROUP:
                    return (entry.gr_name, entry.gr_gid)

        libvirt_group = get_local_libvirt_group()

        if not libvirt_group:
            return

        group, gid = libvirt_group

        if gid not in os.getgroups():
            msg = _HELP_MESSAGE.format(username=getpass.getuser(), groupname=group)
            sys.stdout.write(f"{msg}\n")
