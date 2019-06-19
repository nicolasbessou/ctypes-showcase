#!/usr/bin/env python
__doc__ = """Build script

List of commands:
    - waf help              : Print this list of commands
    - waf distclean         : Clean everything (need to call configure after this command)
    - waf clean             : clean everything (no need to call configure after this command)
    - waf configure         : Set some environment variable (do it only once. Not a every build)
    - waf build             : Build Dll and ctypesgen API
"""

import waflib
import os
import sys
import traceback
import copy
import platform

import json
import itertools
import modulefinder
import time
from os.path import dirname, join, isdir

top  = '.'
out  = '_build'

# *****************************************************************************
# Commands composition
# *****************************************************************************
def help(ctx): print __doc__

# *****************************************************************************
# Configure
# *****************************************************************************
def options(ctx):
    ctx.load('python')
    ctx.load('compiler_c')

def configure(ctx):
    ctx.options.pyc, ctx.options.pyo = 0, 0
    ctx.load('python')
    ctx.load('compiler_c')      # Load C compiler (Use Cl.exe in Windows environment)

    # Gcc version to be used by ctypesgen
    ctx.env.PYTHONSCRIPT = dirname(ctx.env['PYTHON'][0])
    if platform.system() == 'Windows':
        ctx.env.PYTHONSCRIPT = join(ctx.env.PYTHONSCRIPT, 'Scripts')
    try:
        ctx.find_program("gcc", var="GCC", path_list=[ctx.env.PYTHONSCRIPT])
    except :
        ctx.find_program("gcc", var="GCC")
    ctx.env.GCC = ctx.env.GCC[0].replace(os.sep, '/')
    # search for ctypegen.py in PATH environment variable and in ctx.env.PYTHONSCRIPT
    ctypegen_pathlist = os.environ['PATH'].split(':')
    ctypegen_pathlist.append(ctx.env.PYTHONSCRIPT)
    ctx.env.CTYPESGEN = ctx.find_file("ctypesgen.py", path_list=ctypegen_pathlist)

    # Check installed python modules
    ctx.check_python_module('numpy')
    ctx.check_python_module('ctypesgencore')  # Use ctypesgencore because the script does work when checking ctypesgen (since its a script not a lib)

    # Define compilation and link flags in release and debug mode
    if platform.system() == 'Windows':
        # ctx.env.append_unique('DEFINES', "ISGCC_ACLS_DBG_LOGFILE=1")
        cFlags = ['/FS', '/EHsc', '/W3', '/O2', '/MD']
        ctx.env.DLLEXT = 'dll'
        ctx.env.append_unique('CFLAGS'   , cFlags)
        ctx.env.append_unique('CXXFLAGS' , cFlags)
        ctx.env.append_unique('DEFINES'  , 'NDEBUG')

    else:
        cFlags = ['-fvisibility=default', '-Wall', '-Werror', '-Wno-sign-compare', '-Wno-format-security', '-fPIC', '-O2']
        ctx.env.DLLEXT = 'dylib'
        ctx.env.append_unique('CFLAGS'   ,  cFlags + ['-std=c99'  ])
        ctx.env.append_unique('CXXFLAGS' ,  cFlags + ['-std=c++11'])
        ctx.env.append_unique('DEFINES'  , 'NDEBUG')
        ctx.env.append_unique('LINKFLAGS', '-fvisibility=default')


# *****************************************************************************
# Build
# *****************************************************************************
def build(ctx):

    # ******** Select source files, include directories and macros here ********
    # List of source files to compile
    _sources         = [ctx.path.find_resource('algo.c')]

    # List of include directories
    _includes        = [ctx.path.parent.abspath()]

    # List of preprocessor macros
    _defines         = []

    # Header files that needs to be accessible vis python
    _apiHeaders      = [ctx.path.find_resource('algo.h')]

    # Path to the dll to build and to the generated api python module.
    _dllPath         = ctx.path.get_bld().find_or_declare('algo.dll')
    _genApiPath      = ctx.path.get_bld().find_or_declare('genApiAlgo.py')

    # Compile Dll
    ctx.shlib(
        source   = _sources,
        target   = _dllPath,
        defines  = _defines,
        includes = _includes,
        linkflags= [],
        name     = 'Compile DLL'
        )

    # Generate Api
    ctx(
        rule        = makeCtypesGenApi,
        source      = [_dllPath] + _apiHeaders,
        target      = _genApiPath,
        vars        = {'defines':_defines, 'includes':_includes},
        color       = 'CYAN',
        cls_keyword = lambda x:'Generating API',
        cls_str     = lambda x:x.outputs[0].abspath(),
        name        = 'Generate API'
        )

# *****************************************************************************
# Rules
# *****************************************************************************
def makeCtypesGenApi(task):
    """Rule to generate a python module based on a compiled DLL and header files.

    Source = [DLL file, Header files, ...]
    Target = Python API file
    """
    headers = task.inputs[1:]
    dll     = task.inputs[0].abspath()
    out     = task.outputs[0].abspath()
    defines = ' '.join(['-D{}'.format(x) for x in task.vars['defines']])
    cmd     = [
        'python', '-u', task.generator.bld.env.CTYPESGEN,
        '--save-preprocessed-headers=%s' % out + '.preproc.h',
        ' '.join([x.abspath() for x in headers]),
        '-o'   , out,
        '-l'   , dll,
        '--cpp', '"%s -E %s"' % (task.generator.bld.env.GCC, defines),
        '-I'   , task.generator.bld.path.parent.abspath(),
        ]
    for inc in task.vars['includes']:
        cmd.extend(['-I', "%s" % inc])
    cmd = ' '.join(cmd).replace(os.sep, '/')
    outLog = out + '.log'
    waflib.Logs.pprint('YELLOW', 'Executing: {}'.format(cmd))
    waflib.Logs.pprint('YELLOW', 'Log into : {}'.format(outLog))
    with open(outLog, 'w') as f:
        ret = task.exec_command(cmd, stdout=f, stderr=f, cwd=task.generator.bld.path.abspath())
    return ret
