import plyvel

from pydaten.common.transaction import Transaction
from pydaten.common.block import Block
from pydaten.common.address import Address, RawAddress, NameAddress
from pydaten.utils.bytestream import ByteStream
from pydaten.defaults import genesis, config
import struct
class World:
    HEIGHT_PREFIX = b'\x00'

    def __init__(self, path):
        self.root = plyvel.DB(path, create_if_missing = True)

    def get_height(self):
        result = self.root.get(World.HEIGHT_PREFIX)
        return struct.unpack('>L', result)[0] if result else 0
    def set_height(self, wb, height):
        if height > 0:
            wb.put(World.HEIGHT_PREFIX, struct.pack('>L', height))
        else:
            wb.delete(World.HEIGHT_PREFIX)

    def set_transaction(self, wb, index, transaction):
        addr = transaction.address()
        name, rest = addr.pop()
        bs = ByteStream()
        bs.write(b'.'.join([n.encode('ascii') for n in reversed(rest.name)]))
        bs.write(b'|')
        bs.write_uint32(transaction.target)
        bs.write_uint16(index)
        bs.write(name.encode('ascii'))
        k = bs.value()
        wb.put(k, transaction.serialize())
        shortcut = b'.'.join([n.encode('ascii') for n in reversed(addr.name)])
        wb.put(b'\x03' + shortcut, k)
        bs = ByteStream()
        src = self.resolve(transaction.source)
        src.write(bs)
        wb.put(b'\x04' + shortcut, bs.value())
        dst = self.resolve(transaction.destination)
        return k

    def get_transaction(self, name_address):
        shortcut = b'.'.join([n.encode('ascii') for n in reversed(name_address.name)])
        k = self.root.get(b'\x03' + shortcut)
        return Transaction.deserialize(self.root.get(k))
    def clear_transaction(self, wb, name_address):
        shortcut = b'.'.join([n.encode('ascii') for n in reversed(name_address.name)])
        k = self.root.get(b'\x03' + shortcut)
        wb.delete(b'\x03' + shortcut)
        wb.delete(b'\x04' + shortcut)
        wb.delete(k)

    def push_block(self, block):
        height = self.get_height()
        if block.index == height:
            with self.root.write_batch() as wb:
                self.set_height(wb, height + 1)
                self.set_block(wb, block)
        else:
            raise Exception("Block Index mismatch!")
    def pop_block(self):
        latest = self.get_latest_block()
        with self.root.write_batch() as wb:
            self.set_height(wb, self.get_height() - 1)
            self.clear_block(wb, latest.index)
        return latest

    def set_block_header(self, wb, header):
        wb.put(b'\x01' + struct.pack('>L', header.index), header.serialize(header_only = True))
    def get_block_header(self, index):
        return Block.deserialize(self.root.get(b'\x01' + struct.pack('>L', index)), header_only = True)
    def clear_block_header(self, wb, index):
        wb.delete(b'\x01' + struct.pack('>L', index))

    def set_block(self, wb, block):
        self.set_block_header(wb, block)
        balance = {}
        for ind, tx in enumerate(block.transactions):
            k = self.set_transaction(wb, ind, tx)
            wb.put(b'\x02' + struct.pack('>LL', block.index, ind), k)
            src = self.resolve(tx.source)
            dst = self.resolve(tx.destination)
            if src.public_key not in balance:
                balance[src] = 0
            if dst.public_key not in balance:
                balance[dst] = 0
            balance[src] -= (tx.fee + tx.amount)
            balance[dst] += tx.amount
        for raw, bal in balance.items():
            if raw != config.NOWHERE_NAME:
                self.set_balance(wb, raw, self.get_balance(raw) + bal)
    def get_block(self, index):
        block = self.get_block_header(index)
        prefix = b'\x02' + struct.pack('>L', index)
        txs = list(self.root.iterator(prefix = prefix, include_key = False))
        block.transactions = [Transaction.deserialize(self.root.get(tx)) for tx in txs]
        return block
    def clear_block(self, wb, index):
        self.clear_block_header(wb, index)
        prefix = b'\x02' + struct.pack('>L', index)
        balance = {}
        for tx in self.root.iterator(prefix = prefix, include_value = False):
            transact = Transaction.deserialize(self.root.get(self.root.get(tx)))
            addr = transact.address()
            self.clear_transaction(wb, addr)
            src = self.resolve(transact.source)
            dst = self.resolve(transact.destination)
            if src not in balance:
                balance[src] = 0
            if dst not in balance:
                balance[dst] = 0
            balance[src] += (transact.fee + transact.amount)
            balance[dst] -= transact.amount
            wb.delete(tx)
        for raw, bal in balance.items():
            if raw != config.NOWHERE_NAME:
                self.set_balance(wb, raw, self.get_balance(raw) + bal)

    def get_latest_block(self):
        return self.get_block(self.get_height() - 1)

    def get_balance(self, raw_address):
        k = b'\x05' + raw_address.public_key
        result = self.root.get(k)
        return struct.unpack('>Q', result)[0] if result else 0
    def set_balance(self, wb, raw_address, balance):
        k = b'\x05' + raw_address.public_key
        wb.put(k, struct.pack('>Q', balance))

    def resolve(self, address):
        if type(address) is RawAddress:
            return address
        else:
            shortcut = b'.'.join([n.encode('ascii') for n in reversed(address.name)])
            result = self.root.get(b'\x04' + shortcut)
            if result:
                return Address.read(ByteStream(result))
            else:
                raise Exception("Invalid name!")

    def children(self, name_address):
        prefix = b'.'.join([n.encode('ascii') for n in reversed(name_address.name)]) + b'|'
        result = []
        for k, v in self.root.iterator(prefix = prefix):
            result.append(Transaction.deserialize(v))
        return result
