#!/usr/bin/python3

import io
import struct

class ByteStream:

    def __init__(self, raw = None):
        if not raw:
            self._bytes = io.BytesIO()
        else:
            self._bytes = io.BytesIO(raw)

    def write_uint8(self, num):
        self._bytes.write(struct.pack('>B', num))

    def write_uint16(self, num):
        self._bytes.write(struct.pack('>H', num))

    def write_uint32(self, num):
        self._bytes.write(struct.pack('>L', num))

    def write_uint64(self, num):
        self._bytes.write(struct.pack('>Q', num))

    def write(self, raw):
        self._bytes.write(raw)

    def read_uint8(self):
        return struct.unpack('>B', self._bytes.read(1))[0]

    def read_uint16(self):
        return struct.unpack('>H', self._bytes.read(2))[0]

    def read_uint32(self):
        return struct.unpack('>L', self._bytes.read(4))[0]

    def read_uint64(self):
        return struct.unpack('>Q', self._bytes.read(8))[0]

    def read(self, count = None):
        if count is not None:
            return self._bytes.read(count)
        else:
            return self._bytes.read()

    def value(self):
        return self._bytes.getvalue()
