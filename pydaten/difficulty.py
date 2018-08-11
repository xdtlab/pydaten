#!/usr/bin/python3

def less_or_equal(bts_a, bts_b):
    for a, b in zip(bts_a, bts_b):
        if a < b:
            return True
        if a > b:
            return False
    return True

def multiply(bts, numerator, denominator):
    return to_bytes(from_bytes(bts) * numerator // denominator)

def to_bytes(num):
    return num.to_bytes(32, byteorder='big')

def from_bytes(bts):
    if len(bts) != 32:
        raise Exception("Not a 256-bit number!")
    return int.from_bytes(bts, byteorder='big')

def compress(bts):
    if len(bts) != 32:
        raise Exception("Not a 256-bit number!")
    while bts[0] == 0 and len(bts) > 3:
        bts = bts[1:]
    return int.from_bytes(bytes([len(bts)]) + bts[0:3], byteorder='big')

def decompress(num):
    bts = num.to_bytes(4, byteorder='big')
    result = int.from_bytes(bts[0:1], byteorder='big')
    result = bts[1:4] + b'\0' * (result - 3)
    result = b'\0' * (32 - len(result)) + result
    return result

def normalize(bts):
    return decompress(compress(bts))
