#!/usr/bin/python3

import time
import io

from pydaten.utils.bytestream import ByteStream
from pydaten.defaults import config
from pydaten.common.data import Data
from pydaten.common.address import Address, NameAddress

class Transaction:

    def __init__(self, version, target, fee, name, source, destination, amount, data, signature):
        self.version = version
        self.target = target
        self.fee = fee
        self.name = name
        self.source = source
        self.destination = destination
        self.amount = amount
        self.data = data
        self.signature = signature

    def serialize(self, signature_included = True):
        stream = ByteStream()
        stream.write_uint8(self.version)
        stream.write_uint32(self.target)
        stream.write_uint64(self.fee)

        encoded_name = self.name.encode('ascii')
        stream.write_uint8(len(encoded_name))
        stream.write(encoded_name)

        self.source.write(stream)
        self.destination.write(stream)

        stream.write_uint64(self.amount)

        self.data.write(stream)

        if signature_included:
            stream.write_uint8(len(self.signature))
            stream.write(self.signature)

        return stream.value()

    def deserialize(serialized, signature_included = True):
        raw = ByteStream(serialized)

        version = raw.read_uint8()
        target = raw.read_uint32()
        fee = raw.read_uint64()

        name = raw.read(raw.read_uint8()).decode('ascii')

        source = Address.read(raw)
        destination = Address.read(raw)

        amount = raw.read_uint64()

        data = Data.read(raw)

        signature = raw.read(raw.read_uint8()) if signature_included else None

        return Transaction(version, target, fee, name, source, destination, amount, data, signature)

    def address(self):
        return self.destination.push(self.name)

    def calculate_hash(self):
        return config.REGULAR_HASH_FUNCTION(self.serialize())

    def signable(self):
        return self.serialize(signature_included = False)

    def valid(self):
        result = NameAddress.valid_part(self.name)
        return result

    def serialize_list(transactions):
        raw = ByteStream()
        raw.write_uint32(len(transactions))
        for transaction in transactions:
            serialized = transaction.serialize()
            raw.write_uint32(len(serialized))
            raw.write(serialized)
        return raw.value()

    def deserialize_list(serialized):
        transactions = []
        raw = ByteStream(serialized)
        length = raw.read_uint32()
        for i in range(length):
            transaction_size = raw.read_uint32()
            transactions.append(Transaction.deserialize(raw.read(transaction_size)))
        return transactions

if __name__ == '__main__':
    pass
