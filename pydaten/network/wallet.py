#!/usr/bin/python3

import coincurve as cc
import hashlib
import requests
import time
import random

from pydaten.network.lightnode import LightNode
from pydaten.common.transaction import Transaction
from pydaten.defaults import config
from pydaten.common.address import *
from pydaten.common.data import *

class Wallet(LightNode):
    def __init__(self, key = None):
        super().__init__()
        try:
            if key and len(key) == 32:
                self._private_key = cc.PrivateKey(key, context=cc.GLOBAL_CONTEXT)
            elif key:
                raise ValueError()
            else:
                self._private_key = cc.PrivateKey(context=cc.GLOBAL_CONTEXT)
        except ValueError:
            raise ValueError("Key should be 32 bytes!")
        self._public_key = self._private_key.public_key

    def private_key(self):
        return self._private_key.secret

    def public_key(self):
        return self._public_key.format(compressed=True)

    def _sha256(data):
        return hashlib.sha256(data).digest()

    def sign(self, message):
        return self._private_key.sign(message, hasher=Wallet._sha256)

    def verify(address, message, signature):
        return cc.PublicKey(address, context=cc.GLOBAL_CONTEXT) \
            .verify(signature, message, hasher=Wallet._sha256)

    def send_transaction(self, name, destination, amount, data = NoData()):
        peer = random.choice(self.random_peers())
        status = self.get_status_from(peer)
        target = status['height'] + 1
        byte_price = status['bytePrice']
        tx =  Transaction(
            version = config.VERSION, target = target, fee = 0,
            name = name,
            source = RawAddress(self.public_key()),
            destination = destination,
            amount = amount,
            data = data,
            signature = b'\0' * 71)
        tx.fee = byte_price * len(tx.serialize())
        tx.signature = self.sign(tx.signable())
        return self.send_transaction_to(peer, tx)

if __name__ == '__main__':

    key = bytes.fromhex(input("Please enter your key. (Or press enter for a new account)\n"))
    wallet = Wallet(key if key else None)

    print("Address: " + wallet.public_key().hex())
    print("Key: " + wallet.private_key().hex())
