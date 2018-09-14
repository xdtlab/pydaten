#!/usr/bin/python3

import io
import threading
import time
import os
from abc import ABC, abstractmethod

from pydaten.common.transaction import Transaction
from pydaten.common.block import Block
from pydaten.utils import misc
from pydaten.utils.bytestream import ByteStream
from pydaten.core import difficulty
from pydaten.defaults import config, genesis
from pydaten.common.data import NoData
from pydaten.common.address import *
from pydaten.core.errors import *
from pydaten.crypto import ecdsa
from pydaten.core.world import World

class Blockchain(object):

    def __init__(self, path):
        self.world = World(path)
        self.transactions = []
        self.lock = threading.RLock()
        if self.get_height() == 0:
            self.push_block(genesis.genesis_block())

    def get_block(self, index):
        return self.world.get_block(index)

    def get_block_range(self, start, end):
        return [self.get_block(i) for i in range(start, end)]

    def get_blocks(self):
        return self.get_block_range(0, self.get_height())

    def get_latest_block(self):
        return self.world.get_latest_block()

    def get_height(self):
        return self.world.get_height()

    def resolve(self, address):
        try:
            return self.world.resolve(address)
        except:
            return None

    def get_balance(self, raw_address):
        return self.world.get_balance(raw_address)

    def pop_block(self):
        with self.lock:
            popped = self.world.pop_block()
            self.transactions = []
            return popped

    def push_block(self, block):
        with self.lock:
            self.is_next_block(block)
            self.world.push_block(block)
            self.transactions = []

    def calculate_hash_difficulty(self):
        block = self.get_latest_block()
        current_difficulty = difficulty.decompress(block.difficulty)
        if block.index > 0 and block.index % config.DIFFICULTY_ADJUSTMENT_SPAN == 0:
            block_delta = self.get_block(block.index - config.DIFFICULTY_ADJUSTMENT_SPAN)
            timestamp_delta = (block.timestamp - block_delta.timestamp) // config.DIFFICULTY_ADJUSTMENT_SPAN
            numerator, denominator = (timestamp_delta, config.TARGET_TIME_PER_BLOCK)
            if denominator > config.DIFFICULTY_CHANGE_RATIO_LIMIT * numerator:
                numerator, denominator = (1, config.DIFFICULTY_CHANGE_RATIO_LIMIT)
            try:
                new_difficulty = difficulty.normalize(difficulty.multiply(current_difficulty, numerator, denominator))
                if difficulty.less_or_equal(config.MINIMUM_HASH_DIFFICULTY, new_difficulty):
                    new_difficulty = config.MINIMUM_HASH_DIFFICULTY
            except OverflowError:
                new_difficulty = config.MINIMUM_HASH_DIFFICULTY

            return new_difficulty
        else:
            return current_difficulty

    def calculate_reward(self):
        return self.get_balance(config.SUPPLY_NAME) // config.REWARD_DIVISION

    def is_next_block(self, block):
        # Check genesis block
        if self.get_height() == 0 and block == genesis.genesis_block():
            return

        # Check if it is a valid block
        self.is_valid_block(block)

        # Check if it is the next block
        if block.index != self.get_height():
            raise InvalidIndex()

        # Check if it points to the previous block
        if block.previous_hash != self.get_latest_block().calculate_hash():
            raise InvalidPreviousHash()

        # Check if timestamp is logical
        if block.index >= config.BLOCKS_CLOCK_CHECK:
            previous_blocks = self.get_block_range(block.index - config.BLOCKS_CLOCK_CHECK, block.index)
            timestamps = [b.timestamp for b in previous_blocks]
            med = misc.median(timestamps)
            if block.timestamp <= med:
                raise InvalidTimestamp()

        # Check if work has been done on the block
        claimed_difficulty = difficulty.decompress(block.difficulty)
        if claimed_difficulty != self.calculate_hash_difficulty():
            raise InvalidDifficulty()

        # Check if all transactions are valid
        payers = dict()
        hashes = set()
        fees = 0
        for transaction in block.transactions[:-2]:

            # Check if the transaction has minimum validity in this blockchain.
            self.is_valid_transaction(transaction)

            # Check if transaction is targeting this block
            if transaction.target != block.index:
                raise InvalidTransactionTarget()

            # Check if it is not a duplicate transaction
            transaction_hash = transaction.calculate_hash()
            if transaction_hash not in hashes:
                hashes.add(transaction_hash)
            else:
                raise DuplicatedTransactionsFound()

            source = self.resolve(transaction.source)
            destination = self.resolve(transaction.destination)
            if source not in payers:
                payers[source] = 0
            if destination not in payers:
                payers[destination] = 0
            payers[source] += transaction.amount + transaction.fee
            payers[destination] -= transaction.amount

            fees += transaction.fee

        # Check if payers have enough balance
        for payer in payers:
            balance = self.get_balance(payer)
            if payers[payer] > balance:
                raise BalanceNotEnough()

        # Check fee transaction
        fee_transaction = block.transactions[-2]
        if fee_transaction.source != config.NOWHERE_NAME or fee_transaction.amount != fees or self.resolve(fee_transaction.destination) is None:
            raise InvalidFeeTransaction()

        # Check reward transaction
        reward_transaction = block.transactions[-1]
        if reward_transaction.source != config.SUPPLY_NAME or reward_transaction.amount != self.calculate_reward() or self.resolve(reward_transaction.destination) is None:
            raise InvalidRewardTransaction()

    def is_valid_block(self, block):
        # Check block size
        if len(block.serialize()) > config.MAX_BLOCK_SIZE:
            raise BlockTooLarge()

        # Check block validity.
        if not block.valid():
            raise InvalidBlock()

        # Check if it isn't an old block
        if block.index < self.get_height():
            raise BlockOld()

        # Check if minimum PoW has been done on it
        block_hash = block.calculate_hash()
        claimed_difficulty = difficulty.decompress(block.difficulty)

        if not difficulty.less_or_equal(block_hash, claimed_difficulty) or \
            not difficulty.less_or_equal(claimed_difficulty, config.MINIMUM_HASH_DIFFICULTY):
            raise InvalidDifficulty()

        return True

    def fork(self, blocks):
        with self.lock:
            prev_height = self.get_height()
            fork_height = blocks[0].index - 1
            popped = []
            while self.get_height() - 1 != fork_height:
                popped.append(self.pop_block())
            for b in blocks:
                try:
                    self.push_block(b)
                except:
                    break
            if self.get_height() > prev_height:
                return True
            else:
                while self.get_height() - 1 != fork_height:
                    self.pop_block()
                while popped:
                    self.push_block(popped.pop())
                return False

    def is_valid_transaction(self, transaction):
        # Check if transaction structure is valid
        if not transaction.valid():
            raise InvalidTransaction()

        # Check if transaction is supported.
        if transaction.version > config.VERSION:
            raise NotSupportedTransaction()

        # Check if it is in the next blocks
        if transaction.target < self.get_height():
            raise InvalidTransactionTarget()

        # Check if name has not taken yet
        if transaction.name:
            if self.resolve(transaction.address()):
                raise NameTaken()

        # Check if it is signed by the source
        source = self.resolve(transaction.source)
        if source is None:
            raise InvalidTransactionSource()
        if not ecdsa.verify(transaction.signable(), source.public_key, transaction.signature):
            raise InvalidTransactionSignature()
        destination = self.resolve(transaction.destination)
        if destination is None:
            raise InvalidTransactionDestination()

        return True

    def add_transaction(self, transaction):

        # Check if it is a valid transaction
        self.is_valid_transaction(transaction)

        # Check if it is in the next block
        if transaction.target != self.get_height():
            raise InvalidTransactionTarget()

        # Check if it is not a duplicate transaction
        transaction_hash = transaction.calculate_hash()
        for tx in self.transactions:
            if transaction_hash == tx.calculate_hash():
                raise DuplicatedTransactionsFound()

        source = self.resolve(transaction.source)

        # Check if payers have enough balance
        spent = 0
        for tx in self.transactions:
            tx_source = self.resolve(tx.source)
            tx_destination = self.resolve(tx.destination)
            if tx_source == source:
                spent += tx.amount + tx.fee
            if tx_destination == source:
                spent -= tx.amount

        spent += transaction.amount + transaction.fee

        balance = self.get_balance(source)
        if spent > balance:
            raise BalanceNotEnough()

        self.transactions.append(transaction)

    def latest(self, address):
        latest_block = self.get_latest_block()
        address = self.resolve(address)
        history = []
        start = max(latest_block.index - config.QUERY_MAX_BLOCKS, 0)
        end = latest_block.index + 1
        for i in range(start, end):
            block = self.get_block(i)
            for tx in block.transactions:
                src = self.resolve(tx.source)
                dst = self.resolve(tx.destination)
                if src == address or dst == address:
                    history.append(tx)
        return history

    def query(self, name = None, destination = None):
        # This is a very huge query.
        if name is None and destination is None:
            return []
        elif name is None and destination is not None:
            return self.world.children(destination)
        elif name is not None and destination is not None:
            return [self.world.get_transaction(destination.push(name))]
        elif name is not None and destination is None:
            return [self.world.get_transaction(NameAddress((name,)))]

    def new_block(self, miner, timestamp):

        fees = 0
        for tx in self.transactions:
            fees += tx.fee

        reward = self.calculate_reward()

        latest_block = self.get_latest_block()
        index = latest_block.index + 1
        previous_hash = latest_block.calculate_hash()
        transactions = list(self.transactions)

        # Sort by byte-price.
        transactions.sort(key = lambda t: t.fee / len(t.serialize()))

        fee_transaction = Transaction(
            version = config.VERSION, target = index, fee = 0,
            name = misc.random_name(),
            source = config.NOWHERE_NAME,
            destination = miner,
            amount = fees,
            data = NoData(),
            signature = b'')
        transactions.append(fee_transaction)

        reward_transaction = Transaction(
            version = config.VERSION, target = index, fee = 0,
            name = misc.random_name(),
            source = config.SUPPLY_NAME,
            destination = miner,
            amount = reward,
            data = NoData(),
            signature = b'')
        transactions.append(reward_transaction)

        diff = self.calculate_hash_difficulty()
        compressed_diff = difficulty.compress(diff)

        next_block = Block(index, timestamp, previous_hash, compressed_diff, transactions, 0)

        while len(next_block.serialize()) > config.MAX_BLOCK_SIZE:
            tx = next_block.transactions.pop(0)
            fee_transaction.amount -= tx.fee
        next_block.update_merkle_root()

        return next_block

    def mine_block(block):
        diff = difficulty.decompress(block.difficulty)
        block.nonce = 0
        while not difficulty.less_or_equal(block.calculate_hash(), diff):
            block.nonce += 1
