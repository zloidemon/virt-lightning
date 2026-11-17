"""
Translation between a libvirt domain and the init_system metadata.
"""

from virt_lightning.init_system_compat import import_init_system


def _get_gateway(network, network_name):
    if not network_name:
        return None
    try:
        return network.get_network_gateway(network_name)
    except AttributeError:
        #
        # The network does not exist (yet).
        #
        return None


def build_metadata(domain, network):
    """
    Build the init_system metadata of a libvirt domain.
    """
    init_system = import_init_system()

    nics = []
    for i, nic in enumerate(domain.nics):
        nics.append(
            init_system.NetworkInterface(
                name=f"eth{i}",
                mac=nic.get("mac"),
                ipv4=nic.get("ipv4"),
                network=nic.get("network"),
                gateway=_get_gateway(network, nic.get("network")),
            )
        )

    return init_system.InstanceMetadata(
        name=domain.name,
        uuid=domain.dom.UUIDString(),
        fqdn=domain.fqdn,
        user_data=domain.user_data,
        ssh_key=domain.ssh_key,
        root_password=domain.root_password,
        nics=nics,
        dns=network.dns,
    )
