import os
import tempfile
import unittest

from dupefind.core import find_duplicates, wasted_bytes


class DupeFindTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.base = self.dir.name

    def tearDown(self):
        self.dir.cleanup()

    def _write(self, rel: str, data: bytes) -> str:
        path = os.path.join(self.base, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(data)
        return os.path.normpath(path)

    def test_finds_identical_files(self):
        a = self._write("a.bin", b"x" * 100)
        b = self._write("sub/b.bin", b"x" * 100)
        groups = find_duplicates([self.base])
        self.assertEqual(len(groups), 1)
        self.assertEqual(set(groups[0].files), {a, b})

    def test_different_content_is_not_duplicate(self):
        self._write("a.bin", b"x" * 100)
        self._write("b.bin", b"y" * 100)
        self.assertEqual(find_duplicates([self.base]), [])

    def test_min_size_filters_small_files(self):
        self._write("a.bin", b"x" * 10)
        self._write("b.bin", b"x" * 10)
        self.assertEqual(find_duplicates([self.base], min_size=100), [])

    def test_wasted_bytes_counts_all_but_first(self):
        self._write("a.bin", b"x" * 100)
        self._write("b.bin", b"x" * 100)
        self._write("c.bin", b"x" * 100)
        groups = find_duplicates([self.base])
        self.assertEqual(wasted_bytes(groups), 200)

    def test_large_files_use_partial_hashing(self):
        data = os.urandom(2 * 1024 * 1024) + b"tail"
        self._write("a.bin", data)
        self._write("b.bin", data)
        groups = find_duplicates([self.base])
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0].files), 2)


if __name__ == "__main__":
    unittest.main()
