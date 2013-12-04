from mock import create_autospec, patch, Mock, MagicMock
import xmlrpclib
import os

from downloads import downloads

class MockServerProxy( Mock ):
    def __init__( self, *args, **kwargs ):
        super(MockServerProxy,self).__init__( *args, **kwargs )
        self.downloads = None

    @property
    def d( self ):
        return self

    def download_list( self ):
        return self.downloads.keys()

    def getorraise( self, dlhash, key ):
        try:
            d = self.downloads[dlhash]
            return d[key]
        except KeyError as e:
            raise xmlrpclib.Fault(-501, '')

    def get_name( self, dlhash ):
        return self.getorraise( dlhash, 'name' )

    def is_active( self, dlhash ):
        return self.getorraise( dlhash, 'active' )

    def get_complete( self, dlhash ):
        return self.getorraise( dlhash, 'complete' )

    def get_directory( self, dlhash ):
        return self.getorraise( dlhash, 'path' )

    def size_files( self, dlhash ):
        f = self.getorraise( dlhash, 'files' )
        return len( f )

    def get_file( self, dlhash, index ):
        return self.getorraise( dlhash, 'files' )[index]

    def get_files( self, dlhash ):
        files = self.getorraise( dlhash, 'files' )
        return [os.path.join(self.get_directory(dlhash),f) for f in files]

    def erase( self, dlhash ):
        print "Removing {}".format(dlhash)
        if dlhash in self.downloads:
            del self.downloads[dlhash]
            return 0
        return 1

    @property
    def system( self ):
        return self
    @property
    def method( self ):
        return self
    def set_key( self, *args ):
        return 0

# Mock up the ServerProxy
ServerProxy = MockServerProxy( xmlrpclib.ServerProxy )


# Multicall Mock
class MultiCall( object ):
    def __init__( self, conn ):
        self.files = []
        self.f = self
        self.conn = conn

    def __getitem__( self, index ):
        return self.files[index]

    def get_path( self, dlhash, index ):
        self.files.append( self.conn.get_file( dlhash, index ) )

    def __call__( self ):
        return self.files
