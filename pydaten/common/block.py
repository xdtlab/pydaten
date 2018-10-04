#!/usr/bin/python3

import time
import hashlib
import io

from pydaten.defaults import config
from pydaten.utils.bytestream import ByteStream
from pydaten.common.transaction import *
from pydaten.common.errors import *
from pydaten.core.merkletree import MerkleTree

class Block(object):

    def __init__(self, index, timestamp, previous_hash, difficulty, transactions, nonce):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.difficulty = difficulty
        self.transactions = transactions
        self.nonce = nonce
        self.update_merkle_root()

    def update_merkle_root(self):
        self.merkle_root = self.calculate_merkle_root() if self.transactions else None

    def serialize(self, header_only = False):
        stream = ByteStream()

        stream.write_uint32(self.index)
        stream.write_uint32(self.timestamp)
        stream.write(self.previous_hash)
        stream.write(self.merkle_root)
        stream.write_uint32(self.difficulty)
        stream.write_uint32(self.nonce)
        if not header_only:
            stream.write(Transaction.serialize_list(self.transactions))

        return stream.value()

    def deserialize(serialized, header_only = False):
        try:
            raw = ByteStream(serialized)

            index = raw.read_uint32()
            timestamp = raw.read_uint32()
            previous_hash = raw.read(32)
            merkle_root = raw.read(32)
            difficulty = raw.read_uint32()
            nonce = raw.read_uint32()
            transactions = None if header_only else Transaction.deserialize_list(raw.read())

            block = Block(index, timestamp, previous_hash, difficulty, transactions, nonce)
            block.merkle_root = merkle_root
            return block
        except:
            raise BlockCorrupted()

    def serialize_list(blocks, header_only = False):
        raw = ByteStream()
        raw.write_uint32(len(blocks))
        for block in blocks:
            serialized = block.serialize(header_only = header_only)
            raw.write_uint32(len(serialized))
            raw.write(serialized)
        return raw.value()

    def deserialize_list(serialized, header_only = False):
        blocks = []
        raw = ByteStream(serialized)
        length = raw.read_uint32()
        for i in range(length):
            block_size = raw.read_uint32()
            blocks.append(Block.deserialize(raw.read(block_size), header_only = header_only))
        return blocks

    def calculate_merkle_root(self):
        tree = MerkleTree([tx.calculate_hash() for tx in self.transactions])
        return tree.get_root()

    def get_merkle_path(self, transaction_hash):
        tree = MerkleTree([tx.calculate_hash() for tx in self.transactions])
        return tree.get_path(transaction_hash)

    def valid(self):
        # Check merkle root
        if self.merkle_root != self.calculate_merkle_root():
            return False
        return True

    def calculate_hash(self):
        header = self.serialize(header_only = True)
        return config.POW_HASH_FUNCTION(header)

    def __eq__(self, other):
        return self.calculate_hash() == other.calculate_hash()

if __name__ == '__main__':
    pass
