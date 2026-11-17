from virt_lightning.disk_auxiliary import AuxiliaryConfigDriveDisk


#
# OpenStack metadata config drive.
#
class AuxiliaryOpenstackInitDisk(AuxiliaryConfigDriveDisk):
    format_module = "openstack"
