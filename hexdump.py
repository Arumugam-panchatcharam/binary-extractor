#!/usr/bin/env python

import sys
from os import path
import logging
import argparse
import binascii

PY3 = sys.version_info >= (3, 0)

# --- - /chunking helpers
def chunks(seq, size):
    '''Generator that cuts sequence (bytes, memoryview, etc.)
       into chunks of given size. If `seq` length is not multiply
       of `size`, the lengh of the last chunk returned will be
       less than requested.

       >>> list( chunks([1,2,3,4,5,6,7], 3) )
       [[1, 2, 3], [4, 5, 6], [7]]
    '''
    d, m = divmod(len(seq), size)
    for i in range(d):
        yield seq[i*size:(i+1)*size]
    if m:
        yield seq[d*size:]


def chunkread(f, size):
    '''Generator that reads from file like object. May return less
       data than requested on the last read.'''
    c = f.read(size)
    while len(c):
        yield c
        c = f.read(size)


def genchunks(mixed, size):
    '''Generator to chunk binary sequences or file like objects.
       The size of the last chunk returned may be less than
       requested.'''
    if hasattr(mixed, 'read'):
        return chunkread(mixed, size)
    else:
        return chunks(mixed, size)
# --- - /chunking helpers


def dehex(hextext):
    """
    Convert from hex string to binary data stripping
    whitespaces from `hextext` if necessary.
    """
    if PY3:
        return bytes.fromhex(hextext)
    else:
        hextext = "".join(hextext.split())
        return hextext.decode('hex')


def dump(binary, size=2, sep=' '):
    '''
    Convert binary data (bytes in Python 3 and str in
    Python 2) to hex string like '00 DE AD BE EF'.
    `size` argument specifies length of text chunks
    and `sep` sets chunk separator.
    '''
    hexstr = binascii.hexlify(binary)
    if PY3:
        hexstr = hexstr.decode('ascii')
    return sep.join(chunks(hexstr.upper(), size))


def dumpgen(data, size):
    '''
    Generator that produces strings:

    '00000000: 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ................'
    '''
    generator = genchunks(data, 16)
    prevhexdata = ''
    count = 0
    for addr, d in enumerate(generator):
        hexlify = binascii.hexlify(d)
        if hexlify == prevhexdata:
            prevhexdata = hexlify
            count += 1
            if count == 1:
                print("*")
            continue
        else:
            count = 0

        prevhexdata = hexlify
        
        # 00000000:
        line = '%08X: ' % (addr*16)
        # 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00
        dumpstr = dump(d, size=size)
        line += dumpstr[:8*3]
        if len(d) > 8:  # insert separator if needed
            line += ' ' + dumpstr[8*3:]
        # ................
        # calculate indentation, which may be different for the last line
        pad = 2
        if len(d) < 16:
            pad += 3*(16 - len(d))
        if len(d) <= 8:
            pad += 1
        line += ' '*pad

        for byte in d:
            # printable ASCII range 0x20 to 0x7E
            if not PY3:
                byte = ord(byte)
            if 0x20 <= byte <= 0x7E:
                line += chr(byte)
            else:
                line += '.'
        print(line)

def hexdump_ascii(data, size):
    '''
    Transform binary data to the hex dump text format:

    00000000: 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ................

      [x] data argument as a binary string
      [x] data argument as a file like object

    Returns result depending on the `result` argument:
      'print'     - prints line by line
      'return'    - returns single string
      'generator' - returns generator that produces lines
    '''
    if PY3 and type(data) == str:
        raise TypeError('Abstract unicode data (expected bytes sequence)')

    dumpgen(data, size)

'''
def dump_ascii(infile, size):
    with open(infile, 'rb') as binaryfile:
        chunks = iter(lambda: binaryfile.read(16), b'')
        hexlify = map(binascii.hexlify, chunks)

        prevhexdata = ''
        count = 0
        for addr, hexdata in enumerate(hexlify):
            if hexdata == prevhexdata:
                prevhexdata = hexdata
                count += 1
                if count == 1:
                    print("*")
                continue
            else:
                count = 0

            prevhexdata = hexdata

            offset = '%08X: ' % (addr*16)
            print("{} {}".format(offset, hexdata))
'''

def go(args):
    if not path.exists(args.infile):
        logging.error("%s: I couldn't find this file", args.infile)
        sys.exit(1)

    with open(args.infile, 'rb') as binaryfile:
        hexdump_ascii(binaryfile, int(args.size))
