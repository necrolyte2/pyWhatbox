from mock import patch
from nose.tools import eq_, raises
from nose.util import odict
from copy import deepcopy

from ..whatbox import WhatboxXMLRPC
from xmlrpclib_mock import ServerProxy, MultiCall
from downloads import downloads

from xmlrpclib import Fault
from os.path import join

class TestWhatbox( object ):
    def setUp( self ):
        with patch( 'xmlrpclib.ServerProxy', ServerProxy ) as sp:
            self.inst = WhatboxXMLRPC( '', '', '' )
            self.inst.conn.downloads = deepcopy( downloads )

    def test_get_hashs( self ):
        eq_( downloads.keys(), self.inst.get_hashs() )

    @raises(Fault)
    def test_get_download_name_not_in_downloads( self ):
        self.inst.get_download_name( '' )

    @raises(Fault)
    def test_get_download_path_not_in_downloads( self ):
        self.inst.get_download_path( '' )

    def test_get_download_name( self ):
        h = downloads.keys()[0]
        n = downloads[h]['name']
        eq_( n, self.inst.get_download_name( h ) )

    @raises(Fault)
    def test_get_download_files_not_in_downloads( self ):
        with patch( 'xmlrpclib.MultiCall', MultiCall ) as mc:
            self.inst.get_download_files( '' )

    def test_get_download_files( self ):
        with patch( 'xmlrpclib.MultiCall', MultiCall ) as mc:
            h = downloads.keys()[0]
            n = self.inst.conn.get_files( h )
            eq_( n, self.inst.get_download_files( h ) )

    def test_get_all_files( self ):
        with patch( 'xmlrpclib.MultiCall', MultiCall ) as mc:
            rdict = self.inst.get_all_files()
            tst = odict()
            for d, info in downloads.items():
                # Don't compare path
                tst[d] = info
                tst[d]['files'] = self.inst.conn.get_files(d)

            for k, v in tst.items():
                # Don't compare path key
                eitems = sorted([(j,z) for j,z in v.items() if j != 'path'])
                ritems = sorted(rdict[k].items())
                print eitems
                print ritems
                eq_( eitems, ritems )

    def test_delete_download( self ):
        for h, info in self.inst.conn.downloads.items():
            eq_( 0, self.inst.delete_download( h ) )
        with patch( 'xmlrpclib.MultiCall', MultiCall ) as mc:
            r = self.inst.get_all_files()
            eq_( {}, r )
