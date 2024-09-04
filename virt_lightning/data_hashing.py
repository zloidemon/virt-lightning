import hashlib

from virt_lightning.consts import HashingAlgorithm


class DataHashing:
    def __init__(self, algo, data):
        self.__algo = algo
        self.__data = data
        self.__hash = None

    @property
    def algorithm(self):
        if self.__algo is None:
            raise AttributeError("algorithm must be set before use")

        if not isinstance(self.__algo, HashingAlgorithm):
            raise TypeError("algorithm must be string")

        return self.__algo

    @property
    def length(self):
        if not isinstance(self.__data, bytes):
            raise TypeError("data must be bytes")

        return len(self.__data)

    def calculate(self):
        if self.__hash:
            return self.__hash

        match self.algorithm:
            case HashingAlgorithm.SHA256:
                self.__hash = hashlib.sha256(self.__data)
            case HashingAlgorithm.SHA512:
                self.__hash = hashlib.sha512(self.__data)
            case _:
                raise NotImplementedError(self.algorithm)
        return self.__hash

    def __eq__(self, other):
        if self.algorithm != other.algorithm:
            return False

        if self.length != other.length:
            return False

        return str(self) == str(other)

    def __str__(self):
        return self.calculate().hexdigest()

    def __repr__(self):
        return (
            f"HashingData(length={len(self.__data)},algorithm={self.algorithm.value})"
        )
