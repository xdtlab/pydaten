#!/usr/bin/python3

from pydaten.common.transaction import Transaction
from pydaten.common.block import Block
from pydaten.defaults.config import *
from pydaten.common.data import NoData
from pydaten.common.address import RawAddress

FOUNDER_NAME = RawAddress(bytes.fromhex('02f46d41c945d636e00729e2f3355c7c602e8a3703c1a1db138d9919d79b4e1017'))
FOUNDER_INITIAL_BALANCE = SUPPLY // 10 # 10% of all assets
CONTRIBUTORS_NAME = RawAddress(bytes.fromhex('028190dda77ea5252862d2a86ea1a01b79a4c2b618431ed464bccfe0673e4188c5'))
CONTRIBUTORS_INITIAL_BALANCE = SUPPLY // 5 # 20% of all assets
SUPPLY_INITIAL_BALANCE = SUPPLY - FOUNDER_INITIAL_BALANCE - CONTRIBUTORS_INITIAL_BALANCE
GENESIS_TIMESTAMP = 1514628754
GENESIS_NONCE = 10853

def genesis_block():
    supply_account = Transaction(
        version = 0, target = 0, fee = 0,
        name = None,
        source = NOWHERE_NAME,
        destination = SUPPLY_NAME,
        amount = SUPPLY_INITIAL_BALANCE,
        data = NoData(),
        signature = b'')

    founder_account = Transaction(
        version = 0, target = 0, fee = 0,
        name = None,
        source = NOWHERE_NAME,
        destination = FOUNDER_NAME,
        amount = FOUNDER_INITIAL_BALANCE,
        data = NoData(),
        signature = b'')

    contributors_account = Transaction(
        version = 0, target = 0, fee = 0,
        name = None,
        source = NOWHERE_NAME,
        destination = CONTRIBUTORS_NAME,
        amount = CONTRIBUTORS_INITIAL_BALANCE,
        data = NoData(),
        signature = b'')

    genesis_transactions = [supply_account, founder_account, contributors_account]
    genesis_block = Block(0, GENESIS_TIMESTAMP, b'\0' * 32, MINIMUM_HASH_DIFFICULTY_COMPRESSED, genesis_transactions, GENESIS_NONCE)

    return genesis_block

def mine_genesis_block(diff):
    block = genesis_block()
    while not difficulty.less_or_equal(block.calculate_hash(), diff):
        block.nonce += 1
    return block.nonce

if __name__ == '__main__':
    print('Genesis nonce: {}'.format(mine_genesis_block(MINIMUM_HASH_DIFFICULTY)))
    print('Genesis hash: {}'.format(genesis_block().calculate_hash().hex()))
