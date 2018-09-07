import unittest
from pydaten.crypto import ecdsa

class ECDSATest(unittest.TestCase):

    def test_sign_verify(self):
        for i in range(100):
            prv, pub = ecdsa.generate()
            msg = b'a' * i
            signature = ecdsa.sign(msg, prv)
            self.assertTrue(ecdsa.verify(msg, pub, signature))
            self.assertFalse(ecdsa.verify(msg + b'a', pub, signature))

if __name__ == '__main__':
    unittest.main()
