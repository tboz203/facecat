#!/usr/bin/env python
'''A (horribly mangled) script to hide one file within another.

2013-05-14
A revision of two previous programs to satisfy an assignment for CSC442.
Submitted by team Zeus.

    Usage: ./steg -(bB) -(sr) -o<val> [-i<val>] -w<val> [-h<val>]
            -b      Use the bit method
            -B      Use the byte method
            -s      Store (and hide) data
            -r      Retrieve hidden data
            -o<val> Set offset to <val>
            -i<val> Set interval to <val>
            -w<val> Set wrapper file to <val>
            -h<val> Set hidden file to <val>'''

from __future__ import print_function
from sys import argv

sentinel = bytearray([0x00, 0xff, 0x00, 0x00, 0xff, 0x00])

def error(message=None):
    if message:
        print('[-] Error: ', message)

    print('''\
Usage: ./steg -(bB) -(sr) -o<val> [-i<val>] -w<val> [-h<val>]
        -b      Use the bit method
        -B      Use the byte method
        -s      Store (and hide) data
        -r      Retrieve hidden data
        -o<val> Set offset to <val>
        -i<val> Set interval to <val>
        -w<val> Set wrapper file to <val>
        -h<val> Set hidden file to <val>''')
    exit(1)

def store_B(wrapper_f, hidden_f, offset, interval):
    with open(wrapper_f) as file:
        wrapper = bytearray(file.read())
    with open(hidden_f) as file:
        hidden = bytearray(file.read())

    hidden += sentinel

    for i, byte in enumerate(hidden):
        wrapper[offset + interval*i] = byte

    with open(wrapper_f, 'w') as file:
        file.write(wrapper)

def gethidden(wrapper):
    state = 0
    hidden = bytearray()
    for c in wrapper:
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

def getwrapper_B(wrapper, offset, interval):
    for i in range(offset, len(wrapper), interval):
        yield wrapper[i]

def retrieve_B(wrapper_f, hidden_f, offset, interval):
    with open(wrapper_f) as file:
        wrapper = bytearray(file.read())

    wrapper = getwrapper_B(wrapper, offset, interval)
    gethidden(wrapper)

def getbits(string):
    '''break a string up into its component bits'''
    for c in string:
        for i in range(8):
            yield c & 1
            c >>= 1

def store_b(wrapper_f, hidden_f, offset, interval):
    '''Insert a hidden bytearray into a wrapper bytearray. Does some length
    checking.'''

    with open(wrapper_f) as file:
        wrapper = bytearray(file.read())
    with open(hidden_f) as file:
        hidden = bytearray(file.read())

    hidden += sentinel

    # using some binary logic, set the least significant bit in each byte to a
    # byte from our hidden
    for i, x in enumerate(getbits(hidden)):
        wrapper[offset + i] = wrapper[offset + i] & ~1 | x

    with open(wrapper_f, 'w') as file:
        file.write(wrapper)

def getchunks(string):
    '''Break a string up into reversed 8-byte chunks.'''
    while len(string) >= 8:
        chunk, string = string[:8], string[8:]
        yield reversed(chunk)

def getwrapper_b(wrapper, offset):
    for chunk in getchunks(wrapper[offset:]):
        n = 0
        for c in chunk:
            n <<= 1
            n |= c & 1
        yield n

def retrieve_b(wrapper_f, hidden_f, offset, interval):
    with open(wrapper_f) as file:
        wrapper = bytearray(file.read())

    wrapper = getwrapper_b(wrapper, offset)
    gethidden(wrapper)

if __name__ == '__main__':
    offset = interval = None
    action = None
    wrapper = hidden = None

    if '-b' in argv and '-B' in argv:
        error("Cannot specify both bit method and byte method.")
    if '-b' not in argv and '-B' not in argv:
        error("Must specify either bit method or byte method.")
    if '-s' in argv and '-r' in argv:
        error("Cannot specify both storage and retrieval.")
    if '-s' not in argv and '-r' not in argv:
        error("Must specify either storage or retrieval.")

    if not any(map((lambda x: x[:2] == '-o'), argv)):
        error("Must specify an offset.")
    if '-B' in argv and not any(map((lambda x: x[:2] == '-i'), argv)):
        error("Must specify an interval when using byte method.")
    elif '-b' in argv and any(map((lambda x: x[:2] == '-i'), argv)):
        error("Cannot specify an interval when using bit method.")
    if '-s' in argv and not any(map((lambda x: x[:2] == '-h'), argv)):
        error("Must pass a file to hide when storing.")
    elif '-r' in argv and any(map((lambda x: x[:2] == '-h'), argv)):
        error("Cannot pass a file to hide when retrieving.")

    if '-b' in argv and '-s' in argv:
        action = store_b
    if '-b' in argv and '-r' in argv:
        action = retrieve_b
    if '-B' in argv and '-s' in argv:
        action = store_B
    if '-B' in argv and '-r' in argv:
        action = retrieve_B

    for arg in argv[1:]:
        if arg[:2] == '-o':
            offset = int(arg[2:])
        elif arg[:2] == '-i':
            interval = int(arg[2:])
        elif arg[:2] == '-w':
            wrapper = arg[2:]
        elif arg[:2] == '-h':
            hidden = arg[2:]

    action(wrapper, hidden, offset, interval)
