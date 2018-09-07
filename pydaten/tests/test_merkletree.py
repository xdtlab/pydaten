import unittest
import hashlib
from pydaten.core.merkletree import MerkleTree
from pydaten.core.errors import HashNotFound

class MerkleTreeTest(unittest.TestCase):

    def test_verify_path(self):
        for i in range(1, 32):
            hashes = []
            for j in range(i):
                hashes.append(hashlib.sha256(bytes([j])).digest())
            tree = MerkleTree(hashes)
            for h in hashes:
                path = tree.get_path(h)
                self.assertTrue(tree.verify_path(h, path))
            non_existing = hashlib.sha256(bytes([i])).digest()
            with self.assertRaises(HashNotFound):
                tree.get_path(non_existing)

if __name__ == '__main__':
    unittest.main()
