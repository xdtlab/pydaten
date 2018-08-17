#!/usr/bin/python3
import requests
import random
import threading
import time

from . import config
from .block import Block
from .blockchain import Blockchain

class LightNode:

    PEERS_URL = "{}/peers"
    STATUS_URL = "{}/status"
    TRANSACTIONS_URL = "{}/transactions"
    BLOCK_URL = "{}/blocks/{}"
    BLOCKS_RANGE_URL = "{}/blocks/{}/{}"
    BLOCKS_URL = "{}/blocks"
    TRANSACTION_HISTORY_URL = "{}/address/{}/transactions"
    BALANCE_URL = "{}/address/{}/balance"

    def __init__(self, initial_peers):
        self.bad_peers = {}
        self.peers = set(initial_peers)
        self.peers_lock = threading.Lock()

    def all_peers(self):
        return self.peers - self.bad_peers.keys()

    def random_peers(self):
        good_peers = self.all_peers()
        count = min(len(good_peers), config.MAX_PEERS)
        return random.sample(good_peers, count)

    def set_bad_peer(self, peer):
        self.bad_peers[peer] = int(time.time())

    def clear_bad_peers(self):
        expired = []
        now = int(time.time())
        for p, t in self.bad_peers.items():
            if now - t > config.BAD_PEER_BAN_TIME:
                expired.append(p)
        for p in expired:
            del self.bad_peers[p]

    def update_peers(self):
        self.clear_bad_peers()
        new_peers = set()
        for node in self.all_peers():
            try:
                response = requests.get(LightNode.PEERS_URL.format(node))
                if response.status_code == 200:
                    result = response.json()
                    new_peers = new_peers.union(result["peers"])
                    new_peers.add(node)
            except requests.exceptions.RequestException as e:
                self.set_bad_peer(node)
        with self.peers_lock:
            self.peers = new_peers

    def add_peer(self, peer):
        with self.peers_lock:
            self.peers.add(peer)

    def get_block_from(self, index, peer, header_only = False):
        url = self.BLOCK_URL.format(peer, index)
        if header_only:
            url += '?header'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                block = Block.deserialize(requests.get(url).content, header_only = header_only)
                return block
        except requests.exceptions.RequestException as re:
            self.set_bad_peer(node)

    def get_block(self, index, header_only = False):
        hashes = set()
        blocks = []
        for node in self.peers:
            block = self.get_block_from(index, node, header_only)
            if block:
                block_hash = block.calculate_hash()
                if block_hash not in hashes:
                    blocks.append(block)
                    hashes.add(block_hash)
        return blocks

    def get_status_from(self, peer):
        url = self.STATUS_URL.format(peer)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException as re:
            self.set_bad_peer(node)

    def get_block_range_from(self, start, end, peer, header_only = False):
        url = self.BLOCKS_RANGE_URL.format(peer, start, end)
        if header_only:
            url += '?header'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                blocks = Block.deserialize_list(requests.get(url).content, header_only = header_only)
                return blocks
        except requests.exceptions.RequestException as re:
            self.set_bad_peer(node)

    def send_transaction_to(self, peer, transaction):
        url = LightNode.TRANSACTIONS_URL.format(peer)
        try:
            response = requests.post(url, data = transaction.serialize())
            return response.json()
        except requests.exceptions.RequestException:
            self.set_bad_peer(node)

if __name__ == '__main__':
    ln = LightNode()
    ln.update_peers()
