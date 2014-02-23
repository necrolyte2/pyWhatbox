#!/usr/bin/env python2

from whatbox import WhatboxXMLRPC
import argparse
import os.path
import os
import re
import subprocess
import shlex
import sys

# Default url path to finished downloads
# on the host
PRIVATEFINISHED='/private/finished'

# Whatbox instance
what = None

def main():
    global what
    args = parse_args()
    what = WhatboxXMLRPC( args.host, args.username, args.password, args.xmlpath )

    alldls = what.get_all_files()
    if args.hashs:
        hashs = {h:alldls[h] for h in args.hashs}
    else:
        hashs = alldls

    sync_completed( args.username, args.password, args.host, args.xmlpath, args.destdir, args.finishedpath, hashs )

def sync_completed( username, password, host, xmlpath, syncdir, finishedpath, torrents ):
    if finishedpath != '/':
        finishedpath += '/'
    basesyncurl = 'https://{}{}'.format(host, finishedpath)

    for dlhash, info in torrents.items():
        if info['complete'] == 1:
            sync_torrent( (dlhash,info), basesyncurl, syncdir, username, password )

def should_download( download_path ):
    ''' Filter downloads and check for their existence '''
    exclude_filter = ('.torrent','.txt','.jpg','.nfo','.meta')
    if os.path.exists( download_path ):
        return False
    p,e = os.path.splitext( download_path )
    if e in exclude_filter:
        return False

    return True

def sync_torrent( torrent, baseurl, syncdir, username, password, conns=16 ):
    dlhash, torrent_info = torrent
    if baseurl[-1] != '/':
        baseurl = baseurl + '/'
        
    dstdir = os.path.join( syncdir, torrent_info['name'] )
    try:
        os.mkdir( dstdir )
    except OSError as e:
        if e.errno == 17:
            pass
        else:
            raise e

    downloads = []
    failed = False
    # Loop through all files in the torrent
    for f in torrent_info['files']:
        # Split the file name up by each /
        p = f.split('/')
        # We only want the portion of the filename that comes after the name of the torrent
        r = "/".join( p[p.index( torrent_info['name'] ):] )
        path, filename = os.path.split( r )
        if should_download( os.path.join( dstdir, filename ) ):
            url = baseurl + r
            # Would probably be best to just urllib to download the chunks for a more full python solution
            cmd = 'aria2c --file-allocation=none -k 10M -s {conns} -j {conns} -x {conns} '\
                '--http-user {username} --http-pass {password} --check-certificate=false "{url}"'.format(
                    conns=conns, username=username, password=password, url=url
            )
            try:
                p = subprocess.Popen( shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=dstdir )
            except OSError as e:
                print "Please install aria2c"
                sys.exit( -1 )
            for line in iter(p.stdout.readline, b''):
                print line.rstrip()
            # Wait for the process to finish
            p.wait()
            if p.returncode != 0:
                print "{} failed".format(cmd)
                print "return code was {}".format(p.returncode)
                failed = True
    # Should check to make sure it is actually downloaded now
    if not failed:
        what.delete_download( dlhash )

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
        dest='destdir',
        help='Directory to sync downloads to'
    )
    parser.add_argument(
        '-p',
        default='/xmlrpc',
        dest='xmlpath'
    )
    parser.add_argument(
        '--hash',
        dest='hashs',
        nargs='*',
        default=[],
        help='Hashs to download or do them all if not specified'
    )
    parser.add_argument(
        '--fp',
        default=PRIVATEFINISHED,
        dest='finishedpath',
        help='The url path(part after hostname) to finished downloads[Default:{}]'.format(PRIVATEFINISHED)
    )

    return parser.parse_args()

if __name__ == '__main__':
    main()
