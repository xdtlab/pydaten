#!/usr/bin/python3
from . import config
from .bytestream import ByteStream
from .errors import HashNotFound

class MerkleNode:
    def __init__(self, value, left, right, parent):
        self.value = value
        self.left = left
        self.right = right
        self.parent = parent

class MerkleTree:

    def __init__(self, hashes):
        self._leaves = [MerkleNode(h, None, None, None) for h in hashes]
        nodes = self._leaves
        while len(nodes) > 1:
            new_layer = []
            for i in range(len(nodes) // 2):
                a = nodes[i * 2]
                b = nodes[i * 2 + 1]
                new_hash = config.REGULAR_HASH_FUNCTION(a.value + b.value)
                parent = MerkleNode(new_hash, None, None, None)
                a.parent = b.parent = parent
                a.right = b
                b.left = a
                new_layer.append(parent)
            if len(nodes) % 2 == 1:
                last = nodes[-1]
                new_layer.append(last)
            nodes = new_layer
        self._root = nodes[0]

    def get_root(self):
        return self._root.value

    def get_path(self, hashed):
        found = None
        for node in self._leaves:
            if node.value == hashed:
                found = node
                break
        if not found:
            raise HashNotFound()
        output = ByteStream()
        start = node
        while start.parent:
            output.write_uint8(0 if start.right else 1)
            output.write(start.right.value if start.right else start.left.value)
            start = start.parent
        return output.value()

    def verify_path(self, start, path):
        stream = ByteStream(path)
        try:
            while True:
                d = stream.read_uint8()
                h = stream.read(32)
                if d == 0:
                    start = config.REGULAR_HASH_FUNCTION(start + h)
                elif d == 1:
                    start = config.REGULAR_HASH_FUNCTION(h + start)
                else:
                    return False
        except:
            return start == self._root.value
