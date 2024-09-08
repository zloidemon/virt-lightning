from pathlib import PosixPath


class ConfigurationOCIBuild:
    def __init__(self, configuration):
        self.__configuration = configuration

    @classmethod
    def load(cls, src):
        match (src.scheme, src.netloc):
            case "", "":
                path_to_file = PosixPath(src.geturl())
                print(path_to_file)
            case "http" | "https", _:
                raise NotImplementedError(f"HTTP: {src.scheme} not supported")
            case _:
                raise NotImplementedError(f"source: {src.scheme} not supported")
#        return cls(configuration)
        return cls()
