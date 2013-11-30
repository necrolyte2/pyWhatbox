from mock import create_autospec, patch, Mock, MagicMock
import xmlrpclib
import os

from downloads import downloads

def getorraise( dlhash, key ):
    try:
        d = downloads[dlhash]
        return d[key]
    except KeyError as e:
        raise xmlrpclib.Fault(-501, '')

def getname( dlhash ):
    return getorraise( dlhash, 'name' )

def getactive( dlhash ):
    return getorraise( dlhash, 'active' )

def getcomplete( dlhash ):
    return getorraise( dlhash, 'complete' )

def getpath( dlhash ):
    return getorraise( dlhash, 'path' )

def sizefiles( dlhash ):
    f = getorraise( dlhash, 'files' )
    return len( f )

def getfile( dlhash, index ):
    return getorraise( dlhash, 'files' )[index]

def getfiles( dlhash ):
    files = getorraise( dlhash, 'files' )
    return [os.path.join(getpath(dlhash),f) for f in files]

# Mock up the ServerProxy
conn = Mock( xmlrpclib.ServerProxy )
conn.return_value.download_list.return_value = downloads.keys()
conn.return_value.d.get_name = Mock( side_effect=getname )
conn.return_value.d.get_directory = Mock( side_effect=getpath )
conn.return_value.d.is_active = Mock( side_effect=getactive )
conn.return_value.d.get_complete = Mock( side_effect=getcomplete )
conn.return_value.d.size_files = Mock( side_effect=sizefiles )

# Alias for importing
ServerProxy = conn


# Multicall Mock
class MultiCall( object ):
    def __init__( self, conn ):
        self.files = []
        self.f = self

    def __getitem__( self, index ):
        return self.files[index]

    def get_path( self, dlhash, index ):
        self.files.append( getfile( dlhash, index ) )

    def __call__( self ):
        return self.files
