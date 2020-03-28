#!/usr/bin/env python

import os
import argparse
import sys
import pkg_resources
import logging


PY3 = sys.version_info >= (3, 0)

if PY3:
    import configparser
else:
    import ConfigParser

# Custom imports
import hexdump

# TODO: This is temporary before migrating to sdist
__version__ = '1.0'
__author__  = 'arumugam panchatcharam  <arumugamece2013@gmail.com>'
__license__ = 'MIT'

config_sections = list()
config_lookup = dict()

parser = argparse.ArgumentParser(prog='binextractor', description='Extract Data from Binary based on structure information provided')
parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))
subparsers = parser.add_subparsers()
#
shared_parser = argparse.ArgumentParser(add_help=False)
shared_parser.add_argument('--conf', dest='conf', default='default.conf', help='Binary data config file', metavar='BININFO')
#
hexdump_parser = subparsers.add_parser('hexdump', description='Hexdump Binary File', parents=[shared_parser])
hexdump_parser.add_argument('-i', '--infile', dest='infile', required=True, help='Input file to process', metavar='INFILE')
hexdump_parser.add_argument('-s', '--size', dest='size', default=2, help='1-Byte, 2-half word, 4-word', metavar='SIZE')
hexdump_parser.add_argument('-l', '--length', dest='length', default=0xFFFFFFFF, help='Length upto to hexdmp binary file', metavar='LENGTH')
hexdump_parser.set_defaults(function=hexdump.go)
#

def ParseConfig(config_file):
    # check if 'config.ini' file present
    if os.path.isfile(config_file):
        if PY3:
            config = configparser.RawConfigParser(inline_comment_prefixes=';')
        else:
            config = ConfigParser.RawConfigParser(inline_comment_prefixes=';')

        config.read(config_file)
    else:
        print("Config File not present!")
        sys.exit(1)

    for sections in config.sections():
        config_sections.append(sections)

    for section in config_sections:
        config_lookup[section] = dict(config[section])

    print("Data type Size",config_lookup['data_type_size'])
    print("Data type Keyword",config_lookup['data_type_keyword'])
    print("Endianness",config_lookup['endiannes']['little-endian'])
    print("Logging",config_lookup['logging']['level'])

def main():
    args = parser.parse_args()

    # Initialize everything with config File
    ParseConfig('config.ini')

    # Initialize Logging
    loglevel = logging.NOTSET
    if config_lookup['logging']['level'] == 'DEV':
        # Enable All logs motor mouth :)
        loglevel = logging.DEBUG
    elif config_lookup['logging']['level'] == 'PROD':
        # Log errors only
        loglevel = logging.ERROR
    
    logging.basicConfig(format='[%(levelname)s] %(message)s - %(filename)s +%(lineno)d', level=loglevel)
    
    # launch the subcommand of interest #
    args.function(args)

if __name__=='__main__':
    main()
