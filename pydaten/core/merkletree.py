#!/usr/bin/python3
from pydaten.defaults import config
from pydaten.utils.bytestream import ByteStream
from pydaten.core.errors import HashNotFound

class MerkleNode:
    def __init__(self, value, neighbour, parent):
        self.value = value
        self.neighbour = neighbour
        self.parent = parent

class MerkleTree:

    def __init__(self, hashes):
        self._leaves = [MerkleNode(h, None, None) for h in hashes]
        nodes = self._leaves
        while len(nodes) > 1:
            new_layer = []
            for i in range(len(nodes) // 2):
                a = nodes[i * 2]
                b = nodes[i * 2 + 1]
                a, b = (a, b) if a.value < b.value else (b, a)
                new_hash = config.REGULAR_HASH_FUNCTION(a.value + b.value)
                parent = MerkleNode(new_hash, None, None)
                a.parent = b.parent = parent
                a.neighbour = b
                b.neighbour = a
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
            output.write(start.neighbour.value)
            start = start.parent
        return output.value()

    def verify_path(self, start, path):
        stream = ByteStream(path)
        while True:
            h = stream.read(32)
            if len(h) != 32:
                break
            start, h = (start, h) if start < h else (h, start)
            start = config.REGULAR_HASH_FUNCTION(start + h)
        return start == self._root.value
