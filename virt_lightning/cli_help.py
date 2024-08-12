import os


class CLIHelp:
    def __init__(self, action_subparsers, parent_parser):
        pass

    @staticmethod
    def run():
        import getpass

        def get_local_libvirt_group():
            for entry in grp.getgrall():
                if entry.gr_name == consts.DEFAULT_LIBVIRT_GROUP:
                    return (entry.gr_name, entry.gr_gid)

        libvirt_group = get_local_libvirt_group()

        if not libvirt_group:
            return

        group, gid = libvirt_group
        if gid not in os.getgroups():
            print("Virt-Lightning cannot access the local libvirt service.")  # noqa: T001
            print(  # noqa: T001
                f"Your user should probably be in the {group} group. "
                f"You can add the user {getpass. getuser()} in the group {group} with the "
                "following command:"
            )
            print(  # noqa: T001
                f"    sudo usermod --append --groups libvirt {getpass.getuser()}"
            )
