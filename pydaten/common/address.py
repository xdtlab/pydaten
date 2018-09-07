#!/usr/bin/python3

import string
from abc import ABC, abstractmethod

from pydaten.utils.bytestream import ByteStream

class Address(ABC):

    ADDRESS_TYPES = { }

    @abstractmethod
    def write(self, stream):
        stream.write_uint8(self.TYPE_ID)

    @classmethod
    @abstractmethod
    def read(cls, stream):
        type_id = stream.read_uint8()
        return Address.ADDRESS_TYPES[type_id].read(stream)

    @abstractmethod
    def push(self, name):
        pass

    @classmethod
    def from_string(cls, address):
        if len(address) == 66 and all(c in string.hexdigits for c in address):
            return RawAddress(bytes.fromhex(address))
        else:
            return NameAddress(tuple(address.split('.')))

class RawAddress(Address):

    TYPE_ID = 0

    def __init__(self, public_key):
        self.public_key = public_key

    def write(self, stream):
        super().write(stream)
        stream.write(self.public_key)

    @classmethod
    def read(cls, stream):
        return RawAddress(stream.read(33))

    def push(self, name):
        return NameAddress((name,))

    def __str__(self):
        return self.public_key.hex()

    def __eq__(self, other):
        return type(other) is RawAddress and self.public_key == other.public_key

    def __hash__(self):
        return hash(self.public_key)

Address.ADDRESS_TYPES[RawAddress.TYPE_ID] = RawAddress

class NameAddress(Address):

    TYPE_ID = 1

    def __init__(self, name):
        self.name = name

    def write(self, stream):
        super().write(stream)
        stream.write_uint8(len(self.name))
        for part in self.name:
            encoded = part.encode('ascii')
            stream.write_uint8(len(encoded))
            stream.write(encoded)

    @classmethod
    def read(cls, stream):
        parts = []
        parts_count = stream.read_uint8()
        for i in range(parts_count):
            parts.append(stream.read(stream.read_uint8()).decode('ascii'))
        return NameAddress(tuple(parts))

    def push(self, name):
        return NameAddress((name,) + self.name)

    def pop(self):
        return (self.name[0], NameAddress(self.name[1:]))

    def __str__(self):
        return '.'.join(self.name)

    def __eq__(self, other):
        return type(other) is NameAddress and self.name == other.name

    def __hash__(self):
        return hash(self.name)

Address.ADDRESS_TYPES[NameAddress.TYPE_ID] = NameAddress
