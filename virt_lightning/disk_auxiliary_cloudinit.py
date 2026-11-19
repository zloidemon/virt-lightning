from virt_lightning.disk_auxiliary import AuxiliaryConfigDriveDisk


#
# NoCloud/cloud-init config drive.
#
class AuxiliaryCloudInitDisk(AuxiliaryConfigDriveDisk):
    format_module = "cloudinit"
