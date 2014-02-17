#!/usr/bin/env python
# hide.py
# tboz203 - 2014/02/04
#
# A few functions to do some steganography

from __future__ import print_function

import subprocess
import struct

sentinel = bytearray('\x00\xff\x00\x00\xff\x00')

def generate_image():
    '''Use the ImageMagick command `convert` to generate a randomized image.'''
    conv_args = ['convert', '-size', '960x960', 'plasma:fractal', 'jpeg:-']

    # in production, we need to check this for errors, but here it's fine.
    # question: what happens if victim machine doesn't have ImageMagick?
    data = subprocess.check_output(conv_args)

    return data

def _gethidden(container):
    state = 0
    hidden = bytearray()
    for c in container:
        hidden.append(c)

        if state == 0 and c == 0x00:
            state = 1
        elif state == 1:
            if c == 0x00:
                state = 1
            elif c == 0xff:
                state = 2
            else:
                state = 0
        elif state == 2 and c == 0x00:
            state = 3
        elif state == 3 and c == 0x00:
            state = 4
        elif state == 4:
            if c == 0x00:
                state = 1
            elif c == 0xff:
                state = 5
            else:
                state = 0
        elif state == 5 and c == 0x00:
            break
        else:
            state = 0

    print(hidden[:-6])

def _getbits(string):
    # break a string up into its component bits
    for c in string:
        for i in range(8):
            yield c & 1
            c >>= 1

def _getchunks(string):
    # Break a string up into reversed 8-byte chunks.
    while len(string) >= 8:
        chunk, string = string[:8], string[8:]
        yield reversed(chunk)

def _getcontainer(container, offset):
    for chunk in _getchunks(container[offset:]):
        n = 0
        for c in chunk:
            n <<= 1
            n |= c & 1
        yield n

def store(container, hidden, offset=1022, skip=64):
    '''Insert a hidden bytearray into a container bytearray. Does some length
    checking.'''

    # with open(container_f) as file:
    #     container = bytearray(file.read())
    # with open(hidden_f) as file:
    #     hidden = bytearray(file.read())

    container = bytearray(container)

    # is this all we need to do? do we need to check for sentinel w/in string
    # and escape it?
    hidden += sentinel

    # using some binary logic, set the least significant bit in each byte to a
    # byte from our hidden
    for i, x in enumerate(_getbits(hidden)):
        container[offset + i*(skip+1)] = container[offset + i*(skip+1)] & ~1 | x

    return container

def retrieve(container, hidden, offset=1024):
    '''Retrieve a hidden bytearray from a container bytearray.'''

    # with open(container_f) as file:
    #     container = bytearray(file.read())

    container = _getcontainer(container, offset)
    return _gethidden(container)
