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
        self.conn = xmlrpclib.ServerProxy( url )

    def get_hashs( self ):
        '''
            Returns a list of all torrent hashes
        '''
        return self.conn.download_list()

    def get_download_name( self, dlhash ):
        '''
            Returns the name of a given torrent hash

            @param dlhash - The hash to fetch the name for
            @returns the name of the torrent
        '''
        return self.conn.d.get_name( dlhash )

    def get_download_path( self, dlhash ):
        '''
            Gets the path of the given torrent hash

            @param dlhash - The hash to fetch the path for
            @returns the path on the server the download is going to
        '''
        return self.conn.d.get_directory( dlhash )

    def get_download_files( self, dlhash ):
        '''
            Gets a list of all the files for a given torrent hash
            @param dlhash - The torrent hash to get the filenames for
            @returns a list of all the paths to the files for the torrent
        '''
        mc = xmlrpclib.MultiCall(self.conn)
        filenames = []
        dlpath = self.get_download_path( dlhash )
        for index in range(self.conn.d.size_files( dlhash )):
            mc.f.get_path( dlhash, index )

        return [os.path.join(dlpath,fn) for fn in mc()]

    def get_all_files( self ):
        '''
            Returns a dictionary of information about all torrents on the server
            @returns a dictionary keyed by each torrent hash with information about
                each of the torrents
        '''
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

    def delete_download( self, dlhash ):
        '''
            Sets the event to delete the download when the torrent is erased
            The documentation is not exactly the most straight forward so I can
            only hope this is the easiest/best way to do it.

            @param dlhash

            @returns the return code from running the commands
        '''
        ret = self.conn.system.method.set_key( 
                'event.download.erased',
                'removefile',
                'execute={rm,-rf,$d.get_base_path=}'
        )
        if ret == 0:
            ret = self.conn.d.erase( dlhash )
        return ret
