import unittest

from virt_lightning.consts import HashingAlgorithm
from virt_lightning.data_hashing import DataHashing


class TestOCIAssemblyDataHashing(unittest.TestCase):
    def test_none_algorithm(self):
        with self.assertRaises(AttributeError):
            self.assertIsNotNone(DataHashing(None, b"test").calculate())

    def test_bool_algorithm(self):
        with self.assertRaises(TypeError):
            self.assertIsNotNone(DataHashing(True, b"test").calculate())
        with self.assertRaises(TypeError):
            self.assertIsNotNone(DataHashing(False, b"test").calculate())

    def test_not_implemented_algorithm(self):
        with self.assertRaises(NotImplementedError):
            self.assertIsNotNone(DataHashing(HashingAlgorithm.MD5, b"test").calculate())

    def test_unknown_algorithm(self):
        with self.assertRaises(AttributeError):
            self.assertIsNotNone(DataHashing(HashingAlgorithm.SHA1, b"test").calculate())

    def test_invalid_algorithm_property(self):
        with self.assertRaises(AttributeError):
            self.assertIsNotNone(DataHashing(None, b"test").algorithm)

    def test_valid_algorithm_property(self):
        self.assertEqual(
            HashingAlgorithm.SHA256,
            DataHashing(HashingAlgorithm.SHA256, b"test").algorithm
        )
        self.assertEqual(
            HashingAlgorithm.SHA512,
            DataHashing(HashingAlgorithm.SHA512, b"test").algorithm
        )

    def test_valid_length_property(self):
        self.assertEqual(4, DataHashing(HashingAlgorithm.SHA256, b"test").length)
        self.assertEqual(4, DataHashing(HashingAlgorithm.SHA512, b"test").length)

    def test_none_data_property(self):
        with self.assertRaises(TypeError):
            self.assertIsNotNone(DataHashing(HashingAlgorithm.SHA256, None).length)

    def test_invalid_data_property(self):
        with self.assertRaises(TypeError):
            self.assertIsNotNone(DataHashing(HashingAlgorithm.SHA256, "").length)
        with self.assertRaises(TypeError):
            self.assertIsNotNone(DataHashing(HashingAlgorithm.SHA256, 1234).length)
        with self.assertRaises(TypeError):
            self.assertIsNotNone(DataHashing(HashingAlgorithm.SHA256, True).length)

    def test_invalid_data_type(self):
        with self.assertRaises(TypeError):
            self.assertIsNotNone(DataHashing(HashingAlgorithm.SHA256, "test").calculate())
        with self.assertRaises(TypeError):
            self.assertIsNotNone(DataHashing(HashingAlgorithm.SHA256, None).calculate())
        with self.assertRaises(TypeError):
            self.assertIsNotNone(DataHashing(HashingAlgorithm.SHA256, True).calculate())
        with self.assertRaises(TypeError):
            self.assertIsNotNone(DataHashing(HashingAlgorithm.SHA256, 1234).calculate())

    def test_cached(self):
        hashed = DataHashing(HashingAlgorithm.SHA256, b"test")
        self.assertIsNone(hashed._DataHashing__hash)
        self.assertIsNotNone(hashed.calculate())
        self.assertIsNotNone(hashed._DataHashing__hash)
        self.assertEqual(
            hashed._DataHashing__hash.hexdigest(),
            "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        )
        self.assertEqual(
            hashed.calculate().hexdigest(),
            hashed._DataHashing__hash.hexdigest()
        )
        self.assertEqual(
            str(hashed),
            hashed._DataHashing__hash.hexdigest()
        )

    def check_algo_eq(self, algo):
        hashed = DataHashing(algo, b"test")
        self.assertEqual(
            str(DataHashing(algo, b"test")),
            str(hashed)
        )
        self.assertEqual(
            str(DataHashing(algo, b"test")),
            hashed.calculate().hexdigest()
        )
        self.assertEqual(
            DataHashing(algo, b"test").calculate().hexdigest(),
            hashed.calculate().hexdigest()
        )

    def test_eq(self):
        sha256_data_1 = DataHashing(HashingAlgorithm.SHA256, b"test")
        sha256_data_2 = DataHashing(HashingAlgorithm.SHA256, b"test")

        self.assertEqual(sha256_data_1, sha256_data_2)
        self.assertEqual(sha256_data_2, sha256_data_1)

    def test_sha256_eq(self):
        self.check_algo_eq(HashingAlgorithm.SHA256)

    def test_sha512_eq(self):
        self.check_algo_eq(HashingAlgorithm.SHA512)

    def test_not_eq_algo(self):
        sha256_data = DataHashing(HashingAlgorithm.SHA256, b"test")
        sha512_data = DataHashing(HashingAlgorithm.SHA512, b"test")

        self.assertNotEqual(sha256_data, sha512_data)
        self.assertNotEqual(sha512_data, sha256_data)

    def test_not_eq_length(self):
        sha256_data_1 = DataHashing(HashingAlgorithm.SHA256, b"test")
        sha256_data_2 = DataHashing(HashingAlgorithm.SHA256, b"test2")

        self.assertNotEqual(sha256_data_1, sha256_data_2)
        self.assertNotEqual(sha256_data_2, sha256_data_1)

    def test_sha256_str(self):
        self.assertEqual(
            str(DataHashing(HashingAlgorithm.SHA256, b"test")),
            "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        )

    def test_sha512_str(self):
        self.assertEqual(
            str(DataHashing(HashingAlgorithm.SHA512, b"test")),
            "ee26b0dd4af7e749aa1a8ee3c10ae9923f618980772e473f8819a5d4940e0db2"
            "7ac185f8a0e1d5f84f88bc887fd67b143732c304cc5fa9ad8e6f57f50028a8ff"
        )

    def test_repr(self):
        hashed = DataHashing(HashingAlgorithm.SHA256, b"test")
        self.assertEqual(
            f"HashingData(length={hashed.length},algorithm={hashed.algorithm.value})",
            repr(hashed)
        )
