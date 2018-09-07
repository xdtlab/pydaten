#!/usr/bin/python3

from abc import ABC, abstractmethod

from pydaten.defaults import config
from pydaten.utils.bytestream import ByteStream

class Data(ABC):

    DATA_TYPES = { }

    @abstractmethod
    def write(self, stream):
        stream.write_uint8(self.TYPE_ID)

    @classmethod
    @abstractmethod
    def read(cls, stream):
        type_id = stream.read_uint8()
        return Data.DATA_TYPES[type_id].read(stream)

    def calculate_hash(self):
        writer = ByteStream()
        self.write(writer)
        return config.REGULAR_HASH_FUNCTION(writer.value())

class NoData(Data):

    TYPE_ID = 0

    def __init__(self):
        pass

    def write(self, stream):
        super().write(stream)

    @classmethod
    def read(cls, stream):
        return NoData()

Data.DATA_TYPES[NoData.TYPE_ID] = NoData

class StringData(Data):

    TYPE_ID = 1

    def __init__(self, string):
        self.string = string

    def write(self, stream):
        super().write(stream)
        utf8 = self.string.encode('utf-8')
        stream.write_uint16(len(utf8))
        stream.write(utf8)

    @classmethod
    def read(cls, stream):
        length = stream.read_uint16()
        return StringData(stream.read(length).decode('utf-8'))

Data.DATA_TYPES[StringData.TYPE_ID] = StringData

class BlobData(Data):

    TYPE_ID = 2

    def __init__(self, blob):
        self.blob = blob

    def write(self, stream):
        super().write(stream)
        stream.write_uint16(len(self.blob))
        stream.write(self.blob)

    @classmethod
    def read(cls, stream):
        length = stream.read_uint16()
        return BlobData(stream.read(length))

Data.DATA_TYPES[BlobData.TYPE_ID] = BlobData

class DecimalData(Data):

    TYPE_ID = 3

    def __init__(self, decimal):
        self.decimal = decimal

    def write(self, stream):
        super().write(stream)
        stream.write_uint64(self.decimal)

    @classmethod
    def read(cls, stream):
        return DecimalData(stream.read_uint64())

Data.DATA_TYPES[DecimalData.TYPE_ID] = DecimalData

class BooleanData(Data):

    TYPE_ID = 4

    def __init__(self, boolean):
        self.boolean = boolean

    def write(self, stream):
        super().write(stream)
        stream.write_uint8(1 if self.boolean else 0)

    @classmethod
    def read(cls, stream):
        return BooleanData(stream.read_uint8() == 1)

Data.DATA_TYPES[BooleanData.TYPE_ID] = BooleanData

class ListData(Data):

    TYPE_ID = 5

    def __init__(self, items):
        self.items = items

    def write(self, stream):
        super().write(stream)
        stream.write_uint16(len(self.items))
        for item in self.items:
            item.write(stream)

    @classmethod
    def read(cls, stream):
        length = stream.read_uint16()
        items = []
        for i in range(length):
            items.append(Data.read(stream))
        return ListData(items)

Data.DATA_TYPES[ListData.TYPE_ID] = ListData

class MapData(Data):

    TYPE_ID = 6

    def __init__(self, pairs):
        self.pairs = pairs

    def write(self, stream):
        super().write(stream)
        stream.write_uint16(len(self.pairs))
        for k, v in self.pairs:
            k.write(stream)
            v.write(stream)

    @classmethod
    def read(cls, stream):
        length = stream.read_uint16()
        pairs = []
        for i in range(length):
            k = Data.read(stream)
            v = Data.read(stream)
            pairs.append([k, v])
        return MapData(pairs)

Data.DATA_TYPES[MapData.TYPE_ID] = MapData

if __name__ == '__main__':
    writer = ByteStream()
    dat = ListData([NoData(),
                    BooleanData(True),
                    DecimalData(123),
                    StringData('abc'),
                    BlobData(b'def'),
                    StringData('ghi'),
                    MapData([[BlobData(b'def'), StringData('ghi')],
                                [BlobData(b'def'), StringData('ghi')]])])
    print(dat.calculate_hash().hex())
