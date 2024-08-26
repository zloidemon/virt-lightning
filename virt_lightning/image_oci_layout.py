class OCIImageLayout:
    def __init__(self, data):
        self.__data = data

    @property
    def version(self):
        return self.__data["imageLayoutVersion"]
