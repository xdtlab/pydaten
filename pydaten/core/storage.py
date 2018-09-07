#!/usr/bin/python3

import os
import io
from pydaten.common.block import Block

class FileStorage:

    def __init__(self, path):
        self.path = path

    def save(self, block):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        file_name = os.path.join(self.path, 'block' + str(block.index))
        with io.open(file_name, mode='bw') as f:
            f.write(block.serialize())

    def load(self, index):
        file_name = os.path.join(self.path, 'block' + str(index))
        if os.path.exists(file_name):
            with io.open(file_name, mode='br') as f:
                return Block.deserialize(f.read())
        else:
            raise BlockNotFound()

class MemoryStorage:

    def __init__(self, blocks = []):
        self.blocks = {b.index:b for b in blocks}

    def save(self, block):
        self.blocks[block.index] = block

    def load(self, index):
        if index in self.blocks:
            return self.blocks[index]
        else:
            raise BlockNotFound()

import collections

class CachedStorage:

    def __init__(self, storage, capacity = 128):
        self.storage = storage
        self.capacity = capacity
        self.cache = collections.OrderedDict()

    def save(self, block):
        self.storage.save(block)

    def load(self, index):
        try:
            block = self.cache.pop(index)
        except KeyError:
            block = self.storage.load(index)
        self.cache[index] = block
        if len(self.cache) > self.capacity:
            self.cache.popitem(last = False)
        return block
