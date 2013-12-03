from mock import patch
from nose.tools import eq_, raises
from nose.util import odict

from ..whatbox import WhatboxXMLRPC
from xmlrpclib_mock import ServerProxy, MultiCall, getfiles
from downloads import downloads

from xmlrpclib import Fault
from os.path import join

class TestWhatbox( object ):
    def setUp( self ):
        with patch( 'xmlrpclib.ServerProxy', ServerProxy ) as sp:
            self.inst = WhatboxXMLRPC( '', '', '' )

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
            n = getfiles( h )
            eq_( n, self.inst.get_download_files( h ) )

    def test_get_all_files( self ):
        with patch( 'xmlrpclib.MultiCall', MultiCall ) as mc:
            rdict = self.inst.get_all_files()
            tst = odict()
            for d, info in downloads.items():
                # Don't compare path
                tst[d] = info
                tst[d]['files'] = getfiles(d)

            for k, v in tst.items():
                # Don't compare path key
                eitems = sorted([(j,z) for j,z in v.items() if j != 'path'])
                ritems = sorted(rdict[k].items())
                print eitems
                print ritems
                eq_( eitems, ritems )

