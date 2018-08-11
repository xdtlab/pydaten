import unittest
from .. import difficulty

class DifficultyTest(unittest.TestCase):

    def test_compress_decompress(self):
        for i in range(32):
            diff = b'\0' * i + b'\x2e' + b'\0' * (31 - i)
            self.assertEquals(diff, difficulty.decompress(difficulty.compress(diff)))

if __name__ == '__main__':
    unittest.main()
