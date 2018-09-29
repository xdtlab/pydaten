#!/usr/bin/python3

import aiohttp
from aiohttp import web
import requests
import threading
import string
import sys
import time
import json
import io
import asyncio
import subprocess
import os
from queue import Queue
import pkg_resources

from pydaten.network.lightnode import LightNode
from pydaten.core.blockchain import Blockchain
from pydaten.common.transaction import Transaction
from pydaten.common.block import Block
from pydaten.defaults import config
from pydaten.core import difficulty
from pydaten.defaults import genesis
from pydaten.utils import misc
from pydaten.core.errors import *
from pydaten.common.address import *

RESOURCES_PATH = pkg_resources.resource_filename(__name__, 'resources')

class Node(LightNode):

    @web.middleware
    async def access_control_allow_origin(request, handler):
        resp = await handler(request)
        resp.headers['ACCESS-CONTROL-ALLOW-ORIGIN'] = '*'
        return resp

    def __init__(self, host, ip, port, path, initial_peers, username, password):
        super().__init__(initial_peers)

        self.path = path
        self.host = host
        self.username = username
        self.password = password

        print("Loading the blockchain...")
        self.blockchain = Blockchain(self.path)

        print("Starting a full-node on " + self.host + "...")
        self.block_queue = Queue()
        self.transaction_queue = Queue()
        self.transaction_pool = {}
        self.next_block = None

        self.mining_interrupt = threading.Condition()

        self.network_time_offset = 0

        self.byte_price = 0

        self.listeners = {}
        self.miner = None

        threading.Thread(target=self.heartbeat, daemon=True).start()
        threading.Thread(target=self.block_broadcaster, daemon=True).start()
        threading.Thread(target=self.transaction_broadcaster, daemon=True).start()

        app = web.Application(middlewares=[Node.access_control_allow_origin])

        app.router.add_static('/static/', path = os.path.join(RESOURCES_PATH, 'static'))
        app.router.add_get('/', self.index)
        app.router.add_route('*', '/blocks', self.blocks)
        app.router.add_get('/blocks/{index}', self.block)
        app.router.add_get('/blocks/{start}/{end}', self.block_range)
        app.router.add_route('*', '/peers', self.nodes)
        app.router.add_route('*', '/transactions', self.transactions)
        app.router.add_get('/status', self.status)
        app.router.add_get('/query', self.query)
        app.router.add_get('/latest', self.latest)
        app.router.add_get('/resolve', self.resolve)
        app.router.add_get('/confirm', self.confirm)
        app.router.add_get('/live', self.live)
        app.router.add_get('/mine', self.mine)
        self.app = app
        web.run_app(app, host=ip, port=port)

    def update_peers(self):
        if self.host in self.peers:
            self.peers.remove(self.host)
        super().update_peers()
        if self.host in self.peers:
            self.peers.remove(self.host)

    def broadcast_node(self, host):
        for node in self.random_peers():
            url = LightNode.PEERS_URL.format(node)
            try:
                response = requests.post(url, data = {'peer': host})
            except requests.exceptions.RequestException:
                self.set_bad_peer(node)

    def get_time(self):
        return int(time.time()) - self.network_time_offset

    def adjust_network_time(self):
        node_time = self.get_time()
        times = [node_time]
        for node in self.random_peers():
            url = LightNode.STATUS_URL.format(node)
            try:
                response = requests.get(url)
                times.append(response.json()['time'])
            except requests.exceptions.RequestException:
                self.set_bad_peer(node)
        network_time = misc.median(times)
        self.network_time_offset += node_time - network_time

    def broadcast_block(self, block):
        oks = 0
        peers = self.random_peers()
        if len(peers) == 0:
            return (0, 0)
        for node in peers:
            url = LightNode.BLOCKS_URL.format(node)
            try:
                response = requests.post(url, data = block.serialize())
                if response.json()['ok']:
                    oks += 1
            except requests.exceptions.RequestException:
                self.set_bad_peer(node)
        return (oks, len(peers))

    def broadcast_transaction(self, transaction):
        peers = self.random_peers()
        for node in peers:
            url = LightNode.TRANSACTIONS_URL.format(node)
            try:
                response = requests.post(url, data = transaction.serialize())
            except requests.exceptions.RequestException:
                self.set_bad_peer(node)

    def transaction_exists(self, tx):
        for t in self.transaction_pool[tx.target]:
            if t.calculate_hash() == tx.calculate_hash():
                return True
        return False

    async def index(self, request):
        with io.open(os.path.join(RESOURCES_PATH, 'index.html')) as f:
            html = f.read()
        return web.Response(text = html, headers={'content-type':'text/html'})

    async def status(self, request):
        return web.json_response(data = {'height' : self.blockchain.get_height(), 'time' : self.get_time(), 'bytePrice': self.byte_price})

    async def transactions(self, request):
        if request.method == 'GET':
            return web.json_response(data=[tx.json() for tx in self.blockchain.transactions])
        elif request.method == 'POST':
            tx = Transaction.deserialize(await request.content.read())
            try:
                self.blockchain.is_valid_transaction(tx)
                self.transaction_queue.put(tx)
                return web.json_response(data = {'ok' : True})
            except BlockchainException as e:
                return web.json_response(data = {'ok' : False, 'error': str(e)})

    async def nodes(self, request):
        if request.method == 'GET':
            return web.json_response(data = {'ok': True, 'peers': list(self.all_peers())})
        elif request.method == 'POST':
            peer = (await request.post())['peer']
            self.add_peer(peer)
            return web.json_response(data = {'ok' : True})

    async def blocks(self, request):
        if request.method == 'GET':
            return web.Response(text='All blocks')
        elif request.method == 'POST':
            b = Block.deserialize(await request.content.read())
            try:
                self.blockchain.is_valid_block(b)
                self.block_queue.put(b)
                return web.json_response(data = {'ok' : True})
            except BlockchainException as e:
                return web.json_response(data = {'ok' : False, 'error': str(e)})

    async def block(self, request):
        header_only = 'header' in request.query
        index = request.match_info['index']
        if index == 'latest':
            index = self.blockchain.get_height() - 1
        else:
            index = int(index)
        if index < self.blockchain.get_height():
            return web.Response(body=self.blockchain.get_block(index).serialize(header_only = header_only))
        else:
            return web.Response(body=b'')

    async def block_range(self, request):
        header_only = 'header' in request.query
        start = int(request.match_info['start'])
        end = request.match_info['end']
        if end == 'latest':
            end = self.blockchain.get_height()
        else:
            end = int(end) + 1
        if end > start:
            result = self.blockchain.get_block_range(start, end)
        else:
            result = []
        return web.Response(body=Block.serialize_list(result, header_only = header_only))

    async def query(self, request):
        name = request.query.get('name', None)
        destination = request.query.get('destination', None)
        destination = Address.from_string(destination) if destination else None
        txs = self.blockchain.query(name = name, destination = destination)
        return web.Response(body=Transaction.serialize_list(txs))

    async def latest(self, request):
        address = Address.from_string(request.query.get('address'))
        txs = self.blockchain.latest(address = address)
        return web.Response(body=Transaction.serialize_list(txs))

    async def resolve(self, request):
        address = request.query.get('address', None)
        raw_name = self.blockchain.resolve(Address.from_string(address))
        if raw_name is None:
            return web.json_response({'ok': False, 'error': 'Invalid address.'})
        return web.json_response(data = {
            'balance': self.blockchain.get_balance(raw_name)
        })

    async def confirm(self, request):
        index = int(request.query['target'])
        hashed = bytes.fromhex(request.query['hash'])
        try:
            return web.json_response(data = {
                'ok': True,
                'path': self.blockchain.get_block(index).get_merkle_path(hashed).hex()
            })
        except IndexError:
            return web.json_response(data = { 'ok': False, 'error': 'Block not mined yet!' })
        except Exception as e:
            return web.json_response(data = { 'ok': False, 'error': str(e) })

    async def live(self, request):
        address = request.query.get('address', None)
        raw_name = self.blockchain.resolve(Address.from_string(address))
        if not raw_name:
            return web.json_response({'ok': False, 'error': 'Invalid address.'})
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        if raw_name not in self.listeners:
            self.listeners[raw_name] = []
        self.listeners[raw_name].append(ws)
        async for msg in ws:
            pass
        self.listeners[raw_name].remove(ws)
        if len(self.listeners[raw_name]) == 0:
            del self.listeners[raw_name]
        return ws

    def heartbeat(self):
        while True:
            self.update_peers()
            self.broadcast_node(self.host)
            self.adjust_network_time()
            time.sleep(config.HEARTBEAT_INTERVAL)


    def block_broadcaster(self):
        latest_index = self.blockchain.get_latest_block().index
        while True:
            b = self.block_queue.get()
            if b.index > self.blockchain.get_latest_block().index + 1:
                # Synchronize just with that peer!
                self.synchronize()
            else:
                try:
                    ok, total = self.broadcast_block(b)
                    if total and ok / total < 0.5:
                        self.synchronize()
                    else:
                        self.blockchain.push_block(b)
                except:
                    pass
            if latest_index != self.blockchain.get_latest_block().index:
                latest_block = self.blockchain.get_latest_block()
                latest_index = latest_block.index
                print("Block {} - {}".format(latest_block.index,latest_block.calculate_hash().hex()))

            coro = self.mine_next_block()
            asyncio.run_coroutine_threadsafe(coro, self.app.loop)

    def transaction_exists(self, transaction):
        if transaction.target not in self.transaction_pool:
            return False
        for tx in self.transaction_pool[transaction.target]:
            if tx.calculate_hash() == transaction.calculate_hash():
                return True
        return False

    def transaction_broadcaster(self):
        while True:
            tx = self.transaction_queue.get()
            try:
                if tx.target not in self.transaction_pool:
                    self.transaction_pool[tx.target] = []
                if self.transaction_exists(tx):
                    continue
                else:
                    print("New transaction!")
                    self.transaction_pool[tx.target].append(tx)

                raw_name = self.blockchain.resolve(tx.destination)
                if raw_name in self.listeners:
                    for ws in self.listeners[raw_name]:
                        coro = ws.send_bytes(tx.serialize())
                        asyncio.run_coroutine_threadsafe(coro, self.app.loop)
                self.broadcast_transaction(tx)
            except:
                pass

    def synchronize_with(self, peer):
        latest_block = self.blockchain.get_latest_block()
        remote_diff_blocks = self.get_block_range_from(latest_block.index + 1, 'latest', peer)
        if len(remote_diff_blocks) > 0:
            if remote_diff_blocks[0].previous_hash == latest_block.calculate_hash():
                for block in remote_diff_blocks:
                    try:
                        self.blockchain.push_block(block)
                    except:
                        self.set_bad_peer(peer)
                        break
            else:
                for i in range(latest_block.index, 0, -1):
                    block = self.get_block_from(i, peer)
                    remote_diff_blocks.insert(0, block)
                    if block.previous_hash == self.blockchain.get_block(i - 1).calculate_hash():
                        self.blockchain.fork(remote_diff_blocks)
                        break

    def synchronize(self):
        latest_block = self.blockchain.get_latest_block()
        latest_blocks = {}
        for node in self.random_peers():
            remote_block = self.get_block_from('latest', node)
            if remote_block and remote_block.index > latest_block.index:
                if remote_block.index not in latest_blocks:
                    latest_blocks[remote_block.index] = {}
                remote_hash = remote_block.calculate_hash()
                if remote_hash not in latest_blocks[remote_block.index]:
                    latest_blocks[remote_block.index][remote_hash] = []
                latest_blocks[remote_block.index][remote_hash].append(node)
        if len(latest_blocks) > 0:
            for index, hash_nodes in sorted(latest_blocks.items(), reverse=True):
                for hashed, nodes in hash_nodes.items():
                    latest_block = self.blockchain.get_latest_block()
                    if index > latest_block.index:
                        self.synchronize_with(nodes[0])
                    else:
                        return

    def get_next_block(self):
        new_block_index = self.blockchain.get_latest_block().index + 1
        if not self.next_block or self.next_block.index != new_block_index:
            if new_block_index in self.transaction_pool:
                for tx in self.transaction_pool[new_block_index]:
                    try:
                        self.blockchain.add_transaction(tx)
                    except BlockchainException as e:
                        pass
                del self.transaction_pool[new_block_index]
            self.next_block = self.blockchain.new_block(self.miner_address, self.get_time())
        return self.next_block

    async def mine_next_block(self):
        if self.miner is not None:
            block = self.get_next_block()
            await self.miner.send_json({
                'id': block.index,
                'data': block.serialize(header_only = True).hex(),
                'nonceOffset': 76,
                'nonceSize': 4,
                'timestampOffset': 72,
                'timestampSize': 4,
                'target': difficulty.decompress(block.difficulty).hex()
                })

    async def mine(self, request):
        username = request.query.get('username', None)
        password = request.query.get('password', None)
        if username != self.username or password != self.password:
            return web.json_response(data = { 'ok': False, 'error': 'Auth failed!' })

        miner_address = Address.from_string(request.query.get('address', None))
        if self.blockchain.resolve(miner_address) is None:
            return web.json_response(data = {'ok': False, 'error': 'Miner not valid!'})
        self.miner_address = miner_address
        print("Miner: " + str(self.miner_address))

        if self.miner:
            await self.miner.close()
        self.miner = web.WebSocketResponse()
        await self.miner.prepare(request)
        await self.mine_next_block()

        async for msg in self.miner:
            response = msg.json()
            header = Block.deserialize(bytes.fromhex(response['data']), header_only = True)
            self.next_block.nonce = header.nonce
            self.next_block.timestamp = header.timestamp
            try:
                self.blockchain.is_valid_block(self.next_block)
                self.block_queue.put(self.next_block)
            except BlockchainException as e:
                print(e)
                await self.mine_next_block()
