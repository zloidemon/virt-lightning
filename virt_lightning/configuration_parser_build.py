from virt_lightning.iconfiguration_parser import IConfigurationParser


class ConfigurationParserOCIBuild(IConfigurationParser):
    def __init__(self, data):
        self.data = data

    @classmethod
    def parse(cls, data):
        return cls(data)
