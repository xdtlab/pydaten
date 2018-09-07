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
from pydaten.crypto import ecdsa

class Wallet(LightNode):
    def __init__(self, key = None):
        super().__init__()
        try:
            if key and len(key) == 32:
                self.private_key = key
            elif key:
                raise ValueError()
            else:
                self.private_key = ecdsa.generate()[0]
        except ValueError:
            raise ValueError("Key should be 32 bytes!")
        self.public_key = ecdsa.open(self.private_key)

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
        tx.signature = ecdsa.sign(tx.signable(), self.private_key)
        return self.send_transaction_to(peer, tx)

if __name__ == '__main__':

    key = bytes.fromhex(input("Please enter your key. (Or press enter for a new account)\n"))
    wallet = Wallet(key if key else None)

    print("Address: " + wallet.public_key.hex())
    print("Key: " + wallet.private_key.hex())
