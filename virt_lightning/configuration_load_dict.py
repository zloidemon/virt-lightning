class ConfigurationLoadDict:
    def __init__(self, data):
        self.__data = data

    def read(self):
        return (None, self.__data)

    def __repr__(self):
        return "ConfigurationLoadDict()"
