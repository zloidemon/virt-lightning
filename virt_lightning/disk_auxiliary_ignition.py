from virt_lightning.disk_auxiliary import AuxiliaryConfigDriveDisk


#
# Ignition config drive.
#
class AuxiliaryIgnitionDisk(AuxiliaryConfigDriveDisk):
    format_module = "ignition"
