import logging
import sys
import numpy
import platform
import os
import base64
import imp
from os.path import dirname, abspath, join, isdir, isfile
import subprocess
from ctypes import *


logger  = logging.getLogger(__name__)
curdir  = dirname(abspath(__file__))

def runCommand(cmd, msg):
    """Run a shell command."""
    try:
        logger.info(msg)
        logger.debug(subprocess.check_output(cmd, cwd=curdir, stderr=subprocess.STDOUT, shell=True))
    except subprocess.CalledProcessError as e:
        logger.error(e.output)
        raise

def build():
    """Perform build if required."""
    if not isdir(join('_build', 'c4che')):
        runCommand('python waf configure', 'Waf Configure')
    runCommand('python waf build', 'Build Algo')

def main():
    build()
    apiPath = join(curdir, '_build', 'genApiAlgo.py')
    api     = imp.load_source(base64.encodestring(apiPath), apiPath)

    # Create parameters to provide to the function
    array8                   = numpy.array([0,1,2,3,4])
    array16                  = numpy.array([0,1,2,3,4,5,6,7,8,9])
    pu32                     = numpy.array([20] * api.PU32_LENGTH)
    mystruct                 = api.MyStruct()
    mystruct.u8              = 8
    mystruct.u16             = 16
    mystruct.length_of_pu16  = len(array16)
    mystruct.pu16            = array16.astype(numpy.uint16).ctypes.data_as(POINTER(c_uint16))
    mystruct.pu32[:]         = pu32

    # Call the C function
    api.MyFunction(
        byref(mystruct),
        array8.astype(numpy.uint8).ctypes.data_as(POINTER(c_uint8)),
        len(array8),
        )

    # Table manipulation
    width     = 10
    height    = 10
    image     = numpy.array(range(width*height))
    image     = numpy.reshape(image,(width,height))

    # Create tables
    tablein   = (image.flatten()).astype(numpy.uint32)
    tableout  = numpy.empty_like(tablein)

    # Create pointeur of those tables
    ptablein  = tablein.ctypes.data_as(POINTER(c_uint32))
    ptableout = tableout.ctypes.data_as(POINTER(c_uint32))

    # Modify the table
    api.tablefunction(ptablein, ptableout, width, height)

    # Get the image from the pointeur
    imageout  = numpy.ctypeslib.as_array(ptableout, shape = (width,height))

    if (numpy.array_equal(image,imageout-1)):
        print "You did it!!"

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    main()
