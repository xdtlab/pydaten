import coincurve as cc

from pydaten.defaults.config import REGULAR_HASH_FUNCTION

def generate():
    prv = cc.PrivateKey(context = cc.GLOBAL_CONTEXT)
    return (prv.secret, prv.public_key.format(compressed = True))

def open(prv):
    prv = cc.PrivateKey(prv, context = cc.GLOBAL_CONTEXT)
    return prv.public_key.format(compressed = True)

def sign(message, prv):
    prv = cc.PrivateKey(prv, context = cc.GLOBAL_CONTEXT)
    return prv.sign(message, hasher = REGULAR_HASH_FUNCTION)

def verify(message, pub, signature):
    pub = cc.PublicKey(pub, context=cc.GLOBAL_CONTEXT)
    return pub.verify(signature, message, hasher = REGULAR_HASH_FUNCTION)
