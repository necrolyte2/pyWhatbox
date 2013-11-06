from whatbox import WhatboxXMLRPC

import argparse

def main():
    args = parse_args()
    w = WhatboxXMLRPC(
            args.host,
            args.username,
            args.password,
            args.path
    )
    print w.get_all_files()

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        dest='username'
    )
    parser.add_argument(
        dest='password'
    )
    parser.add_argument(
        dest='host'
    )
    parser.add_argument(
	'-p',
        dest='path',
        default='/xmlrpc'
    )

    return parser.parse_args()

if __name__ == '__main__':
    main()
