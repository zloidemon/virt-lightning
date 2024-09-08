from pathlib import PosixPath


class ConfigurationLoadFile:
    def __init__(self, filename):
        self.__filename = filename

    def read(self):
        if not isinstance(self.__filename, PosixPath):
            raise TypeError("configuration file must be PosixPath")

        full_path = self.__filename.expanduser()

        if not full_path.is_file():
            raise FileNotFoundError(f"file not found: {full_path}")

        if self.__filename.suffix == "":
            raise ValueError(f"unknown format of file: {self.__filename.suffix}")

        return (
            self.__filename.suffix.split(".")[-1],
            self.__filename.expanduser().read_text(),
        )

    def __repr__(self):
        return f"ConfigurationLoadFile(filename={self.__filename})"
