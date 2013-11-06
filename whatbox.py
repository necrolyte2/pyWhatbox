import os
import os.path
import sys
import subprocess

try:
    import xmlrpclib
except ImportError:
    print "xmlrpclib not installed"
    sys.exit( 1 )

class WhatboxXMLRPC( object ):
    def __init__( self, host, username, password, path='/xmlrpc' ):
        self.host = host
        self.path = path
        self.username = username
        self.password = password
        self.conn = None
        self._setup()

    def _setup( self ):
        self._setup_conn()

    def _setup_conn( self, **kwargs ):
	url = 'https://{username}:{password}@{host}{path}'.format(
                **self.__dict__
        )
        print url
        self.conn = xmlrpclib.ServerProxy( url )

    def get_hashs( self ):
        return self.conn.download_list()

    def get_download_name( self, dlhash ):
        return self.conn.d.get_name( dlhash )

    def get_download_path( self, dlhash ):
        return self.conn.d.get_directory( dlhash )

    def get_download_files( self, dlhash ):
        mc = xmlrpclib.MultiCall(self.conn)
        filenames = []
        dlpath = self.get_download_path( dlhash )
        for index in range(self.conn.d.size_files( dlhash )):
            mc.f.get_path( dlhash, index )

        return [os.path.join(dlpath,fn) for fn in mc()]

    def get_all_files( self ):
        hashs = self.get_hashs()
        torrents = {}
        for dhash in hashs:
            if dhash not in torrents:
                torrents[dhash] = {}
            torrents[dhash]['name'] = self.get_download_name(dhash)
            torrents[dhash]['files'] = self.get_download_files(dhash)
            torrents[dhash]['active'] = self.conn.d.is_active(dhash)
            torrents[dhash]['complete'] = self.conn.d.get_complete(dhash)
        return torrents
