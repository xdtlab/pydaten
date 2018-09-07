import unittest
import hashlib
import time
from unittest.mock import *
from pydaten.core.blockchain import Blockchain
from pydaten.core.storage import MemoryStorage
from pydaten.common.address import RawAddress, Address
from pydaten.common.block import Block
from pydaten.common.transaction import Transaction
from pydaten.common.data import NoData
from pydaten.defaults import genesis, config
from pydaten.core import difficulty
from pydaten.crypto import ecdsa

class BlockchainTest(unittest.TestCase):

    ALICE_ADDRESS = RawAddress(b'A' * 33)
    BOB_ADDRESS = RawAddress(b'B' * 33)
    CHARLIE_ADDRESS = RawAddress(b'C' * 33)

    TIMER = 0

    def put_block(self, blockchain, name = None, source = config.SUPPLY_NAME, destination = BOB_ADDRESS, amount = 0):
        tx = Transaction(
            version = config.VERSION, target = blockchain.get_height(), fee = 0,
            name = name,
            source = source,
            destination = destination,
            amount = amount,
            data = NoData(),
            signature = b'\0' * 71)
        blockchain.add_transaction(tx)
        block = blockchain.new_block(BlockchainTest.ALICE_ADDRESS, BlockchainTest.TIMER)
        blockchain.push_block(block)
        BlockchainTest.TIMER += 1


    def test_fork(self):
        with patch.object(difficulty,  'less_or_equal', return_value = True) as mock_less_or_equal:
            with patch.object(ecdsa,  'verify', return_value = True) as mock_verify:
                bc1 = Blockchain(MemoryStorage())
                bc2 = Blockchain(MemoryStorage())
                self.put_block(bc1)
                self.put_block(bc1)
                bc2.fork(bc1.get_blocks()[1:])
                self.put_block(bc1)
                self.put_block(bc1)
                self.put_block(bc2)
                self.put_block(bc2)
                self.put_block(bc2)
                self.put_block(bc2)
                bc3 = Blockchain(MemoryStorage(bc1.get_blocks()))
                bc1.fork(bc2.get_blocks()[3:])
                bc3.fork(bc2.get_blocks()[4:])
                self.assertEquals(bc1.get_height(), 7)
                self.assertEquals(bc3.get_height(), 5)

    def test_push_pop_block(self):
        config.MINIMUM_BYTE_PRICE = 0
        with patch.object(difficulty,  'less_or_equal', return_value = True) as mock_less_or_equal:
            with patch.object(ecdsa,  'verify', return_value = True) as mock_verify:
                bc = Blockchain(MemoryStorage())
                self.put_block(bc, None, config.SUPPLY_NAME, BlockchainTest.BOB_ADDRESS, 1000)
                self.assertEquals(bc.get_balance(BlockchainTest.BOB_ADDRESS), 1000)
                self.put_block(bc, None, config.SUPPLY_NAME, BlockchainTest.BOB_ADDRESS, 500)
                self.assertEquals(bc.get_balance(BlockchainTest.BOB_ADDRESS), 1500)
                self.put_block(bc, 'bob', BlockchainTest.BOB_ADDRESS, BlockchainTest.CHARLIE_ADDRESS, 0)
                self.assertEquals(bc.resolve(Address.from_string('bob')), BlockchainTest.BOB_ADDRESS)
                bc.pop_block()
                self.assertIsNone(bc.resolve(Address.from_string('bob')))
                bc.pop_block()
                self.assertEquals(bc.get_balance(BlockchainTest.BOB_ADDRESS), 1000)
                bc.pop_block()
                self.assertEquals(bc.get_balance(BlockchainTest.BOB_ADDRESS), 0)


if __name__ == '__main__':
    unittest.main()
