import plyvel

from pydaten.common.transaction import Transaction
from pydaten.common.block import Block
from pydaten.common.address import Address, RawAddress, NameAddress
from pydaten.utils.bytestream import ByteStream
from pydaten.defaults import genesis, config
import struct

def _tx_key(name_address):
    return b'.'.join([n.encode('ascii') for n in reversed(name_address.name)])

class World:
    HEIGHT_PREFIX = b'\x00'
    HEADER_PREFIX = b'\x01'
    TRANSACTION_PREFIX = b'\x06'
    BLOCK_TRANSACTION_PREFIX = b'\x02'
    SHORTCUT_PREFIX = b'\x03'
    RESOLVE_PREFIX = b'\x04'
    BALANCE_PREFIX = b'\x05'

    def __init__(self, path):
        self.root = plyvel.DB(path, create_if_missing = True, paranoid_checks = True)

    def push_block(self, block):
        height = self.get_height()
        if block.index == height:
            with self.root.write_batch() as wb:
                self._set_height(wb, height + 1)
                self._set_block(wb, block)
        else:
            raise Exception("Block Index mismatch!")
    def pop_block(self):
        latest = self.get_latest_block()
        with self.root.write_batch() as wb:
            self._set_height(wb, self.get_height() - 1)
            self._clear_block(wb, latest.index)
        return latest

    def resolve(self, address):
        if type(address) is RawAddress:
            return address
        else:
            result = self.root.get(World.RESOLVE_PREFIX + _tx_key(address))
            if result:
                return Address.read(ByteStream(result))
            else:
                raise Exception("Invalid name!")

    def children(self, name_address):
        prefix = World.TRANSACTION_PREFIX + _tx_key(name_address) + b'|'
        result = []
        for k, v in self.root.iterator(prefix = prefix):
            result.append(Transaction.deserialize(v))
        return result

    def get_height(self):
        result = self.root.get(World.HEIGHT_PREFIX)
        return struct.unpack('>L', result)[0] if result else 0
    def _set_height(self, wb, height):
        if height > 0:
            wb.put(World.HEIGHT_PREFIX, struct.pack('>L', height))
        else:
            wb.delete(World.HEIGHT_PREFIX)

    def _set_transaction(self, wb, index, transaction):
        addr = transaction.address()
        name, rest = addr.pop()
        bs = ByteStream()
        bs.write(World.TRANSACTION_PREFIX + _tx_key(rest) + b'|')
        bs.write_uint32(transaction.target)
        bs.write_uint16(index)
        bs.write(name.encode('ascii'))
        k = bs.value()
        wb.put(k, transaction.serialize())
        addr_key = _tx_key(addr)
        wb.put(World.SHORTCUT_PREFIX + addr_key, k)
        bs = ByteStream()
        src = self.resolve(transaction.source)
        src.write(bs)
        wb.put(World.RESOLVE_PREFIX + addr_key, bs.value())
        dst = self.resolve(transaction.destination)
        return k
    def get_transaction(self, name_address):
        k = self.root.get(World.SHORTCUT_PREFIX + _tx_key(name_address))
        return Transaction.deserialize(self.root.get(k))
    def _clear_transaction(self, wb, name_address):
        addr_key = _tx_key(name_address)
        k = self.root.get(World.SHORTCUT_PREFIX + addr_key)
        wb.delete(World.SHORTCUT_PREFIX + addr_key)
        wb.delete(World.RESOLVE_PREFIX + addr_key)
        wb.delete(k)

    def _set_block(self, wb, block):
        wb.put(World.HEADER_PREFIX + struct.pack('>L', block.index), block.serialize(header_only = True))
        balance = {}
        for ind, tx in enumerate(block.transactions):
            k = self._set_transaction(wb, ind, tx)
            wb.put(World.BLOCK_TRANSACTION_PREFIX + struct.pack('>LL', block.index, ind), k)
            src = self.resolve(tx.source)
            dst = self.resolve(tx.destination)
            if src not in balance:
                balance[src] = 0
            if dst not in balance:
                balance[dst] = 0
            balance[src] -= (tx.fee + tx.amount)
            balance[dst] += tx.amount
        for raw, bal in balance.items():
            if raw != config.NOWHERE_NAME:
                self._set_balance(wb, raw, self.get_balance(raw) + bal)
    def get_block(self, index):
        block = Block.deserialize(self.root.get(World.HEADER_PREFIX + struct.pack('>L', index)), header_only = True)
        prefix = World.BLOCK_TRANSACTION_PREFIX + struct.pack('>L', index)
        txs = list(self.root.iterator(prefix = prefix, include_key = False))
        block.transactions = [Transaction.deserialize(self.root.get(tx)) for tx in txs]
        return block
    def _clear_block(self, wb, index):
        wb.delete(World.HEADER_PREFIX + struct.pack('>L', index))
        prefix = World.BLOCK_TRANSACTION_PREFIX + struct.pack('>L', index)
        balance = {}
        for tx in self.root.iterator(prefix = prefix, include_value = False):
            transact = Transaction.deserialize(self.root.get(self.root.get(tx)))
            addr = transact.address()
            self._clear_transaction(wb, addr)
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
                self._set_balance(wb, raw, self.get_balance(raw) + bal)
    def get_latest_block(self):
        return self.get_block(self.get_height() - 1)

    def get_balance(self, raw_address):
        k = World.BALANCE_PREFIX + raw_address.public_key
        result = self.root.get(k)
        return struct.unpack('>Q', result)[0] if result else 0
    def _set_balance(self, wb, raw_address, balance):
        k = World.BALANCE_PREFIX + raw_address.public_key
        wb.put(k, struct.pack('>Q', balance))
