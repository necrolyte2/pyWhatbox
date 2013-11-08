from whatbox import WhatboxXMLRPC
import argparse
import os.path
import os
import re
import subprocess
import shlex

# Default url path to finished downloads
# on the host
PRIVATEFINISHED='/private/finished'

def main():
    args = parse_args()
    sync_completed( args.username, args.password, args.host, args.xmlpath, args.destdir, args.finishedpath )

def sync_completed( username, password, host, xmlpath, syncdir, finishedpath ):
    w = WhatboxXMLRPC(
            host,
            username,
            password,
            xmlpath
    )
    
    if finishedpath != '/':
        finishedpath += '/'
    basesyncurl = 'https://{}{}'.format(host, finishedpath)

    torrents = w.get_all_files()
    for hash, info in torrents.items():
        if info['complete'] == 1:
            sync_torrent( info, basesyncurl, syncdir, username, password )

def should_download( download_path ):
    ''' Filter downloads and check for their existence '''
    exclude_filter = ('.torrent','.txt','.jpg','.nfo','.meta')
    if os.path.exists( download_path ):
        return False
    p,e = os.path.splitext( download_path )
    if e in exclude_filter:
        return False

    return True

def sync_torrent( torrent_info, baseurl, syncdir, username, password, conns=16 ):
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
            p = subprocess.Popen( shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=dstdir )
            for line in iter(p.stdout.readline, b''):
                print line.rstrip()
            if p.returncode != 0:
                print "{} failed".format(cmd)
    # Should like check to make sure it is actually downloaded now
    # Then delete the source torrent and files

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
        '--fp',
        default=PRIVATEFINISHED,
        dest='finishedpath',
        help='The url path(part after hostname) to finished downloads[Default:{}]'.format(PRIVATEFINISHED)
    )

    return parser.parse_args()

if __name__ == '__main__':
    main()
