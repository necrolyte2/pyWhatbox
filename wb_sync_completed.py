from whatbox import WhatboxXMLRPC
import argparse
import os.path
import os
import re
import subprocess
import shlex

# Default url path to finished downloads
PRIVATEFINISHED='/private/finished'
'''
{
    'A43732D2405CABECC09D0D8B653044F3D5E9D3A7': {
        'files': [
            '/home/necrolyte2/finished/Despicable.Me.2.2013.DVDRip.XviD-iNViNCiBLE/Despicable.Me.2.2013.DVDRip.XviD-iNViNCiBLE.avi',
            '/home/necrolyte2/finished/Despicable.Me.2.2013.DVDRip.XviD-iNViNCiBLE/Despicable.Me.2.2013.DVDRip.XviD-iNViNCiBLE.nfo',
            '/home/necrolyte2/finished/Despicable.Me.2.2013.DVDRip.XviD-iNViNCiBLE/Torrent Downloaded From ExtraTorrent.com.txt'
        ],
        'active': 1,
        'name': 'Despicable.Me.2.2013.DVDRip.XviD-iNViNCiBLE',
        'complete': 1
    }, 
    '3B7C54C333FEE187CF581E7A74436C97EE012CBC': {
        'files': [
            '/home/necrolyte2/files/Cliffhanger (1993)/Cliffhanger.1993.720p.Bluray.x264.YIFY.mp4',
            '/home/necrolyte2/files/Cliffhanger (1993)/WWW.YIFY-TORRENTS.COM.jpg',
            '/home/necrolyte2/files/Cliffhanger (1993)/Cliffhanger.1993.720p.Bluray.x264.YIFY.srt'
        ],
        'active': 1,
        'name': 'Cliffhanger (1993)',
        'complete': 0
    }
}
'''

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
        if info['completed'] == 1:
            sync_torrent( info, basesyncurl, syncdir, username, password )

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
    for f in torrent_info['files']:
        p = f.split('/')
        r = "/".join( p[p.index( torrent_info['name'] ):] )
        url = baseurl + r
        # Would probably be best to just urllib to download the chunks for a more full python solution
        cmd = 'aria2c --file-allocation=none -k 10M -s {conns} -j {conns} -x {conns} '\
            '--http-user {username} --http-pass {password} --check-certificate=false "{url}"'.format(
                conns=conns, username=username, password=password, url=url
        )
        print cmd
        p = subprocess.Popen( shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=dstdir )
        for line in iter(p.stdout.readline, b''):
            print line.rstrip()
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
