'''Wrapper for libopenmpt.h

Generated with:
/home/mrb/t/python/bin/ctypesgen.py -L bin -I libopenmpt -lopenmpt -o libopenmpt.py libopenmpt/libopenmpt.h

Do not modify this file.
'''

__docformat__ =  'restructuredtext'

# Begin preamble

import ctypes, os, sys
from ctypes import *

_int_types = (c_int16, c_int32)
if hasattr(ctypes, 'c_int64'):
    # Some builds of ctypes apparently do not have c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (c_int64,)
for t in _int_types:
    if sizeof(t) == sizeof(c_size_t):
        c_ptrdiff_t = t
del t
del _int_types

class c_void(Structure):
    # c_void_p is a buggy return type, converting to int, so
    # POINTER(None) == c_void_p is actually written as
    # POINTER(c_void), so it can be treated as a real pointer.
    _fields_ = [('dummy', c_int)]

def POINTER(obj):
    p = ctypes.POINTER(obj)

    # Convert None to a real NULL pointer to work around bugs
    # in how ctypes handles None on 64-bit platforms
    if not isinstance(p.from_param, classmethod):
        def from_param(cls, x):
            if x is None:
                return cls()
            else:
                return x
        p.from_param = classmethod(from_param)

    return p

class UserString:
    def __init__(self, seq):
        if isinstance(seq, basestring):
            self.data = seq
        elif isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
            self.data = str(seq)
    def __str__(self): return str(self.data)
    def __repr__(self): return repr(self.data)
    def __int__(self): return int(self.data)
    def __long__(self): return long(self.data)
    def __float__(self): return float(self.data)
    def __complex__(self): return complex(self.data)
    def __hash__(self): return hash(self.data)

    def __cmp__(self, string):
        if isinstance(string, UserString):
            return cmp(self.data, string.data)
        else:
            return cmp(self.data, string)
    def __contains__(self, char):
        return char in self.data

    def __len__(self): return len(self.data)
    def __getitem__(self, index): return self.__class__(self.data[index])
    def __getslice__(self, start, end):
        start = max(start, 0); end = max(end, 0)
        return self.__class__(self.data[start:end])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        elif isinstance(other, basestring):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + str(other))
    def __radd__(self, other):
        if isinstance(other, basestring):
            return self.__class__(other + self.data)
        else:
            return self.__class__(str(other) + self.data)
    def __mul__(self, n):
        return self.__class__(self.data*n)
    __rmul__ = __mul__
    def __mod__(self, args):
        return self.__class__(self.data % args)

    # the following methods are defined in alphabetical order:
    def capitalize(self): return self.__class__(self.data.capitalize())
    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))
    def count(self, sub, start=0, end=sys.maxint):
        return self.data.count(sub, start, end)
    def decode(self, encoding=None, errors=None): # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.decode(encoding, errors))
            else:
                return self.__class__(self.data.decode(encoding))
        else:
            return self.__class__(self.data.decode())
    def encode(self, encoding=None, errors=None): # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            else:
                return self.__class__(self.data.encode(encoding))
        else:
            return self.__class__(self.data.encode())
    def endswith(self, suffix, start=0, end=sys.maxint):
        return self.data.endswith(suffix, start, end)
    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))
    def find(self, sub, start=0, end=sys.maxint):
        return self.data.find(sub, start, end)
    def index(self, sub, start=0, end=sys.maxint):
        return self.data.index(sub, start, end)
    def isalpha(self): return self.data.isalpha()
    def isalnum(self): return self.data.isalnum()
    def isdecimal(self): return self.data.isdecimal()
    def isdigit(self): return self.data.isdigit()
    def islower(self): return self.data.islower()
    def isnumeric(self): return self.data.isnumeric()
    def isspace(self): return self.data.isspace()
    def istitle(self): return self.data.istitle()
    def isupper(self): return self.data.isupper()
    def join(self, seq): return self.data.join(seq)
    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))
    def lower(self): return self.__class__(self.data.lower())
    def lstrip(self, chars=None): return self.__class__(self.data.lstrip(chars))
    def partition(self, sep):
        return self.data.partition(sep)
    def replace(self, old, new, maxsplit=-1):
        return self.__class__(self.data.replace(old, new, maxsplit))
    def rfind(self, sub, start=0, end=sys.maxint):
        return self.data.rfind(sub, start, end)
    def rindex(self, sub, start=0, end=sys.maxint):
        return self.data.rindex(sub, start, end)
    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))
    def rpartition(self, sep):
        return self.data.rpartition(sep)
    def rstrip(self, chars=None): return self.__class__(self.data.rstrip(chars))
    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)
    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)
    def splitlines(self, keepends=0): return self.data.splitlines(keepends)
    def startswith(self, prefix, start=0, end=sys.maxint):
        return self.data.startswith(prefix, start, end)
    def strip(self, chars=None): return self.__class__(self.data.strip(chars))
    def swapcase(self): return self.__class__(self.data.swapcase())
    def title(self): return self.__class__(self.data.title())
    def translate(self, *args):
        return self.__class__(self.data.translate(*args))
    def upper(self): return self.__class__(self.data.upper())
    def zfill(self, width): return self.__class__(self.data.zfill(width))

class MutableString(UserString):
    """mutable string objects

    Python strings are immutable objects.  This has the advantage, that
    strings may be used as dictionary keys.  If this property isn't needed
    and you insist on changing string values in place instead, you may cheat
    and use MutableString.

    But the purpose of this class is an educational one: to prevent
    people from inventing their own mutable string class derived
    from UserString and than forget thereby to remove (override) the
    __hash__ method inherited from UserString.  This would lead to
    errors that would be very hard to track down.

    A faster and better solution is to rewrite your program using lists."""
    def __init__(self, string=""):
        self.data = string
    def __hash__(self):
        raise TypeError("unhashable type (it is mutable)")
    def __setitem__(self, index, sub):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data): raise IndexError
        self.data = self.data[:index] + sub + self.data[index+1:]
    def __delitem__(self, index):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data): raise IndexError
        self.data = self.data[:index] + self.data[index+1:]
    def __setslice__(self, start, end, sub):
        start = max(start, 0); end = max(end, 0)
        if isinstance(sub, UserString):
            self.data = self.data[:start]+sub.data+self.data[end:]
        elif isinstance(sub, basestring):
            self.data = self.data[:start]+sub+self.data[end:]
        else:
            self.data =  self.data[:start]+str(sub)+self.data[end:]
    def __delslice__(self, start, end):
        start = max(start, 0); end = max(end, 0)
        self.data = self.data[:start] + self.data[end:]
    def immutable(self):
        return UserString(self.data)
    def __iadd__(self, other):
        if isinstance(other, UserString):
            self.data += other.data
        elif isinstance(other, basestring):
            self.data += other
        else:
            self.data += str(other)
        return self
    def __imul__(self, n):
        self.data *= n
        return self

class String(MutableString, Union):

    _fields_ = [('raw', POINTER(c_char)),
                ('data', c_char_p)]

    def __init__(self, obj=""):
        if isinstance(obj, (str, unicode, UserString)):
            self.data = str(obj)
        else:
            self.raw = obj

    def __len__(self):
        return self.data and len(self.data) or 0

    def from_param(cls, obj):
        # Convert None or 0
        if obj is None or obj == 0:
            return cls(POINTER(c_char)())

        # Convert from String
        elif isinstance(obj, String):
            return obj

        # Convert from str
        elif isinstance(obj, str):
            return cls(obj)

        # Convert from c_char_p
        elif isinstance(obj, c_char_p):
            return obj

        # Convert from POINTER(c_char)
        elif isinstance(obj, POINTER(c_char)):
            return obj

        # Convert from raw pointer
        elif isinstance(obj, int):
            return cls(cast(obj, POINTER(c_char)))

        # Convert from object
        else:
            return String.from_param(obj._as_parameter_)
    from_param = classmethod(from_param)

def ReturnString(obj, func=None, arguments=None):
    return String.from_param(obj)

# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to c_void_p.
def UNCHECKED(type):
    if (hasattr(type, "_type_") and isinstance(type._type_, str)
        and type._type_ != "P"):
        return type
    else:
        return c_void_p

# ctypes doesn't have direct support for variadic functions, so we have to write
# our own wrapper class
class _variadic_function(object):
    def __init__(self,func,restype,argtypes):
        self.func=func
        self.func.restype=restype
        self.argtypes=argtypes
    def _as_parameter_(self):
        # So we can pass this variadic function as a function pointer
        return self.func
    def __call__(self,*args):
        fixed_args=[]
        i=0
        for argtype in self.argtypes:
            # Typecheck what we can
            fixed_args.append(argtype.from_param(args[i]))
            i+=1
        return self.func(*fixed_args+list(args[i:]))

# End preamble

_libs = {}
_libdirs = ['bin']

# Begin loader

# ----------------------------------------------------------------------------
# Copyright (c) 2008 David James
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

import os.path, re, sys, glob
import ctypes
import ctypes.util

def _environ_path(name):
    if name in os.environ:
        return os.environ[name].split(":")
    else:
        return []

class LibraryLoader(object):
    def __init__(self):
        self.other_dirs=[]

    def load_library(self,libname):
        """Given the name of a library, load it."""
        paths = self.getpaths(libname)

        for path in paths:
            if os.path.exists(path):
                return self.load(path)

        raise ImportError("%s not found." % libname)

    def load(self,path):
        """Given a path to a library, load it."""
        try:
            # Darwin requires dlopen to be called with mode RTLD_GLOBAL instead
            # of the default RTLD_LOCAL.  Without this, you end up with
            # libraries not being loadable, resulting in "Symbol not found"
            # errors
            if sys.platform == 'darwin':
                return ctypes.CDLL(path, ctypes.RTLD_GLOBAL)
            else:
                return ctypes.cdll.LoadLibrary(path)
        except OSError,e:
            raise ImportError(e)

    def getpaths(self,libname):
        """Return a list of paths where the library might be found."""
        if os.path.isabs(libname):
            yield libname

        else:
            for path in self.getplatformpaths(libname):
                yield path

            path = ctypes.util.find_library(libname)
            if path: yield path

    def getplatformpaths(self, libname):
        return []

# Darwin (Mac OS X)

class DarwinLibraryLoader(LibraryLoader):
    name_formats = ["lib%s.dylib", "lib%s.so", "lib%s.bundle", "%s.dylib",
                "%s.so", "%s.bundle", "%s"]

    def getplatformpaths(self,libname):
        if os.path.pathsep in libname:
            names = [libname]
        else:
            names = [format % libname for format in self.name_formats]

        for dir in self.getdirs(libname):
            for name in names:
                yield os.path.join(dir,name)

    def getdirs(self,libname):
        '''Implements the dylib search as specified in Apple documentation:

        http://developer.apple.com/documentation/DeveloperTools/Conceptual/
            DynamicLibraries/Articles/DynamicLibraryUsageGuidelines.html

        Before commencing the standard search, the method first checks
        the bundle's ``Frameworks`` directory if the application is running
        within a bundle (OS X .app).
        '''

        dyld_fallback_library_path = _environ_path("DYLD_FALLBACK_LIBRARY_PATH")
        if not dyld_fallback_library_path:
            dyld_fallback_library_path = [os.path.expanduser('~/lib'),
                                          '/usr/local/lib', '/usr/lib']

        dirs = []

        if '/' in libname:
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
        else:
            dirs.extend(_environ_path("LD_LIBRARY_PATH"))
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))

        dirs.extend(self.other_dirs)
        dirs.append(".")

        if hasattr(sys, 'frozen') and sys.frozen == 'macosx_app':
            dirs.append(os.path.join(
                os.environ['RESOURCEPATH'],
                '..',
                'Frameworks'))

        dirs.extend(dyld_fallback_library_path)

        return dirs

# Posix

class PosixLibraryLoader(LibraryLoader):
    _ld_so_cache = None

    def _create_ld_so_cache(self):
        # Recreate search path followed by ld.so.  This is going to be
        # slow to build, and incorrect (ld.so uses ld.so.cache, which may
        # not be up-to-date).  Used only as fallback for distros without
        # /sbin/ldconfig.
        #
        # We assume the DT_RPATH and DT_RUNPATH binary sections are omitted.

        directories = []
        for name in ("LD_LIBRARY_PATH",
                     "SHLIB_PATH", # HPUX
                     "LIBPATH", # OS/2, AIX
                     "LIBRARY_PATH", # BE/OS
                    ):
            if name in os.environ:
                directories.extend(os.environ[name].split(os.pathsep))
        directories.extend(self.other_dirs)
        directories.append(".")

        try: directories.extend([dir.strip() for dir in open('/etc/ld.so.conf')])
        except IOError: pass

        directories.extend(['/lib', '/usr/lib', '/lib64', '/usr/lib64'])

        cache = {}
        lib_re = re.compile(r'lib(.*)\.s[ol]')
        ext_re = re.compile(r'\.s[ol]$')
        for dir in directories:
            try:
                for path in glob.glob("%s/*.s[ol]*" % dir):
                    file = os.path.basename(path)

                    # Index by filename
                    if file not in cache:
                        cache[file] = path

                    # Index by library name
                    match = lib_re.match(file)
                    if match:
                        library = match.group(1)
                        if library not in cache:
                            cache[library] = path
            except OSError:
                pass

        self._ld_so_cache = cache

    def getplatformpaths(self, libname):
        if self._ld_so_cache is None:
            self._create_ld_so_cache()

        result = self._ld_so_cache.get(libname)
        if result: yield result

        path = ctypes.util.find_library(libname)
        if path: yield os.path.join("/lib",path)

# Windows

class _WindowsLibrary(object):
    def __init__(self, path):
        self.cdll = ctypes.cdll.LoadLibrary(path)
        self.windll = ctypes.windll.LoadLibrary(path)

    def __getattr__(self, name):
        try: return getattr(self.cdll,name)
        except AttributeError:
            try: return getattr(self.windll,name)
            except AttributeError:
                raise

class WindowsLibraryLoader(LibraryLoader):
    name_formats = ["%s.dll", "lib%s.dll", "%slib.dll"]

    def load_library(self, libname):
        try:
            result = LibraryLoader.load_library(self, libname)
        except ImportError:
            result = None
            if os.path.sep not in libname:
                for name in self.name_formats:
                    try:
                        result = getattr(ctypes.cdll, name % libname)
                        if result:
                            break
                    except WindowsError:
                        result = None
            if result is None:
                try:
                    result = getattr(ctypes.cdll, libname)
                except WindowsError:
                    result = None
            if result is None:
                raise ImportError("%s not found." % libname)
        return result

    def load(self, path):
        return _WindowsLibrary(path)

    def getplatformpaths(self, libname):
        if os.path.sep not in libname:
            for name in self.name_formats:
                dll_in_current_dir = os.path.abspath(name % libname)
                if os.path.exists(dll_in_current_dir):
                    yield dll_in_current_dir
                path = ctypes.util.find_library(name % libname)
                if path:
                    yield path

# Platform switching

# If your value of sys.platform does not appear in this dict, please contact
# the Ctypesgen maintainers.

loaderclass = {
    "darwin":   DarwinLibraryLoader,
    "cygwin":   WindowsLibraryLoader,
    "win32":    WindowsLibraryLoader
}

loader = loaderclass.get(sys.platform, PosixLibraryLoader)()

def add_library_search_dirs(other_dirs):
    loader.other_dirs = other_dirs

load_library = loader.load_library

del loaderclass

# End loader

add_library_search_dirs(['bin'])

# Begin libraries

_libs["openmpt"] = load_library("openmpt")

# 1 libraries
# End libraries

# No modules

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 80
if hasattr(_libs['openmpt'], 'openmpt_get_library_version'):
    openmpt_get_library_version = _libs['openmpt'].openmpt_get_library_version
    openmpt_get_library_version.argtypes = []
    openmpt_get_library_version.restype = c_uint32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 87
if hasattr(_libs['openmpt'], 'openmpt_get_core_version'):
    openmpt_get_core_version = _libs['openmpt'].openmpt_get_core_version
    openmpt_get_core_version.argtypes = []
    openmpt_get_core_version.restype = c_uint32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 108
if hasattr(_libs['openmpt'], 'openmpt_free_string'):
    openmpt_free_string = _libs['openmpt'].openmpt_free_string
    openmpt_free_string.argtypes = [String]
    openmpt_free_string.restype = None

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 121
if hasattr(_libs['openmpt'], 'openmpt_get_string'):
    openmpt_get_string = _libs['openmpt'].openmpt_get_string
    openmpt_get_string.argtypes = [String]
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_get_string.restype = ReturnString
    else:
        openmpt_get_string.restype = String
        openmpt_get_string.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 127
if hasattr(_libs['openmpt'], 'openmpt_get_supported_extensions'):
    openmpt_get_supported_extensions = _libs['openmpt'].openmpt_get_supported_extensions
    openmpt_get_supported_extensions.argtypes = []
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_get_supported_extensions.restype = ReturnString
    else:
        openmpt_get_supported_extensions.restype = String
        openmpt_get_supported_extensions.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 134
if hasattr(_libs['openmpt'], 'openmpt_is_extension_supported'):
    openmpt_is_extension_supported = _libs['openmpt'].openmpt_is_extension_supported
    openmpt_is_extension_supported.argtypes = [String]
    openmpt_is_extension_supported.restype = c_int

openmpt_stream_read_func = CFUNCTYPE(UNCHECKED(c_size_t), POINTER(None), POINTER(None), c_size_t) # /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 149

openmpt_stream_seek_func = CFUNCTYPE(UNCHECKED(c_int), POINTER(None), c_int64, c_int) # /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 161

openmpt_stream_tell_func = CFUNCTYPE(UNCHECKED(c_int64), POINTER(None)) # /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 170

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 198
class struct_openmpt_stream_callbacks(Structure):
    pass

struct_openmpt_stream_callbacks.__slots__ = [
    'read',
    'seek',
    'tell',
]
struct_openmpt_stream_callbacks._fields_ = [
    ('read', openmpt_stream_read_func),
    ('seek', openmpt_stream_seek_func),
    ('tell', openmpt_stream_tell_func),
]

openmpt_stream_callbacks = struct_openmpt_stream_callbacks # /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 198

openmpt_log_func = CFUNCTYPE(UNCHECKED(None), String, POINTER(None)) # /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 205

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 211
if hasattr(_libs['openmpt'], 'openmpt_log_func_default'):
    openmpt_log_func_default = _libs['openmpt'].openmpt_log_func_default
    openmpt_log_func_default.argtypes = [String, POINTER(None)]
    openmpt_log_func_default.restype = None

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 217
if hasattr(_libs['openmpt'], 'openmpt_log_func_silent'):
    openmpt_log_func_silent = _libs['openmpt'].openmpt_log_func_silent
    openmpt_log_func_silent.argtypes = [String, POINTER(None)]
    openmpt_log_func_silent.restype = None

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 228
if hasattr(_libs['openmpt'], 'openmpt_could_open_propability'):
    openmpt_could_open_propability = _libs['openmpt'].openmpt_could_open_propability
    openmpt_could_open_propability.argtypes = [openmpt_stream_callbacks, POINTER(None), c_double, openmpt_log_func, POINTER(None)]
    openmpt_could_open_propability.restype = c_double

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 232
class struct_openmpt_module(Structure):
    pass

openmpt_module = struct_openmpt_module # /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 232

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 237
class struct_openmpt_module_initial_ctl(Structure):
    pass

struct_openmpt_module_initial_ctl.__slots__ = [
    'ctl',
    'value',
]
struct_openmpt_module_initial_ctl._fields_ = [
    ('ctl', String),
    ('value', String),
]

openmpt_module_initial_ctl = struct_openmpt_module_initial_ctl # /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 237

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 239
if hasattr(_libs['openmpt'], 'openmpt_module_create'):
    openmpt_module_create = _libs['openmpt'].openmpt_module_create
    openmpt_module_create.argtypes = [openmpt_stream_callbacks, POINTER(None), openmpt_log_func, POINTER(None), POINTER(openmpt_module_initial_ctl)]
    openmpt_module_create.restype = POINTER(openmpt_module)

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 241
if hasattr(_libs['openmpt'], 'openmpt_module_create_from_memory'):
    openmpt_module_create_from_memory = _libs['openmpt'].openmpt_module_create_from_memory
    openmpt_module_create_from_memory.argtypes = [POINTER(None), c_size_t, openmpt_log_func, POINTER(None), POINTER(openmpt_module_initial_ctl)]
    openmpt_module_create_from_memory.restype = POINTER(openmpt_module)

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 243
if hasattr(_libs['openmpt'], 'openmpt_module_destroy'):
    openmpt_module_destroy = _libs['openmpt'].openmpt_module_destroy
    openmpt_module_destroy.argtypes = [POINTER(openmpt_module)]
    openmpt_module_destroy.restype = None

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 257
if hasattr(_libs['openmpt'], 'openmpt_module_select_subsong'):
    openmpt_module_select_subsong = _libs['openmpt'].openmpt_module_select_subsong
    openmpt_module_select_subsong.argtypes = [POINTER(openmpt_module), c_int32]
    openmpt_module_select_subsong.restype = c_int

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 258
if hasattr(_libs['openmpt'], 'openmpt_module_set_repeat_count'):
    openmpt_module_set_repeat_count = _libs['openmpt'].openmpt_module_set_repeat_count
    openmpt_module_set_repeat_count.argtypes = [POINTER(openmpt_module), c_int32]
    openmpt_module_set_repeat_count.restype = c_int

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 259
if hasattr(_libs['openmpt'], 'openmpt_module_get_repeat_count'):
    openmpt_module_get_repeat_count = _libs['openmpt'].openmpt_module_get_repeat_count
    openmpt_module_get_repeat_count.argtypes = [POINTER(openmpt_module)]
    openmpt_module_get_repeat_count.restype = c_int32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 261
if hasattr(_libs['openmpt'], 'openmpt_module_get_duration_seconds'):
    openmpt_module_get_duration_seconds = _libs['openmpt'].openmpt_module_get_duration_seconds
    openmpt_module_get_duration_seconds.argtypes = [POINTER(openmpt_module)]
    openmpt_module_get_duration_seconds.restype = c_double

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 263
if hasattr(_libs['openmpt'], 'openmpt_module_set_position_seconds'):
    openmpt_module_set_position_seconds = _libs['openmpt'].openmpt_module_set_position_seconds
    openmpt_module_set_position_seconds.argtypes = [POINTER(openmpt_module), c_double]
    openmpt_module_set_position_seconds.restype = c_double

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 264
if hasattr(_libs['openmpt'], 'openmpt_module_get_position_seconds'):
    openmpt_module_get_position_seconds = _libs['openmpt'].openmpt_module_get_position_seconds
    openmpt_module_get_position_seconds.argtypes = [POINTER(openmpt_module)]
    openmpt_module_get_position_seconds.restype = c_double

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 266
if hasattr(_libs['openmpt'], 'openmpt_module_set_position_order_row'):
    openmpt_module_set_position_order_row = _libs['openmpt'].openmpt_module_set_position_order_row
    openmpt_module_set_position_order_row.argtypes = [POINTER(openmpt_module), c_int32, c_int32]
    openmpt_module_set_position_order_row.restype = c_double

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 268
if hasattr(_libs['openmpt'], 'openmpt_module_get_render_param'):
    openmpt_module_get_render_param = _libs['openmpt'].openmpt_module_get_render_param
    openmpt_module_get_render_param.argtypes = [POINTER(openmpt_module), c_int, POINTER(c_int32)]
    openmpt_module_get_render_param.restype = c_int

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 269
if hasattr(_libs['openmpt'], 'openmpt_module_set_render_param'):
    openmpt_module_set_render_param = _libs['openmpt'].openmpt_module_set_render_param
    openmpt_module_set_render_param.argtypes = [POINTER(openmpt_module), c_int, c_int32]
    openmpt_module_set_render_param.restype = c_int

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 271
if hasattr(_libs['openmpt'], 'openmpt_module_read_mono'):
    openmpt_module_read_mono = _libs['openmpt'].openmpt_module_read_mono
    openmpt_module_read_mono.argtypes = [POINTER(openmpt_module), c_int32, c_size_t, POINTER(c_int16)]
    openmpt_module_read_mono.restype = c_size_t

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 272
if hasattr(_libs['openmpt'], 'openmpt_module_read_stereo'):
    openmpt_module_read_stereo = _libs['openmpt'].openmpt_module_read_stereo
    openmpt_module_read_stereo.argtypes = [POINTER(openmpt_module), c_int32, c_size_t, POINTER(c_int16), POINTER(c_int16)]
    openmpt_module_read_stereo.restype = c_size_t

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 273
if hasattr(_libs['openmpt'], 'openmpt_module_read_quad'):
    openmpt_module_read_quad = _libs['openmpt'].openmpt_module_read_quad
    openmpt_module_read_quad.argtypes = [POINTER(openmpt_module), c_int32, c_size_t, POINTER(c_int16), POINTER(c_int16), POINTER(c_int16), POINTER(c_int16)]
    openmpt_module_read_quad.restype = c_size_t

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 274
if hasattr(_libs['openmpt'], 'openmpt_module_read_float_mono'):
    openmpt_module_read_float_mono = _libs['openmpt'].openmpt_module_read_float_mono
    openmpt_module_read_float_mono.argtypes = [POINTER(openmpt_module), c_int32, c_size_t, POINTER(c_float)]
    openmpt_module_read_float_mono.restype = c_size_t

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 275
if hasattr(_libs['openmpt'], 'openmpt_module_read_float_stereo'):
    openmpt_module_read_float_stereo = _libs['openmpt'].openmpt_module_read_float_stereo
    openmpt_module_read_float_stereo.argtypes = [POINTER(openmpt_module), c_int32, c_size_t, POINTER(c_float), POINTER(c_float)]
    openmpt_module_read_float_stereo.restype = c_size_t

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 276
if hasattr(_libs['openmpt'], 'openmpt_module_read_float_quad'):
    openmpt_module_read_float_quad = _libs['openmpt'].openmpt_module_read_float_quad
    openmpt_module_read_float_quad.argtypes = [POINTER(openmpt_module), c_int32, c_size_t, POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float)]
    openmpt_module_read_float_quad.restype = c_size_t

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 277
if hasattr(_libs['openmpt'], 'openmpt_module_read_interleaved_stereo'):
    openmpt_module_read_interleaved_stereo = _libs['openmpt'].openmpt_module_read_interleaved_stereo
    openmpt_module_read_interleaved_stereo.argtypes = [POINTER(openmpt_module), c_int32, c_size_t, POINTER(c_int16)]
    openmpt_module_read_interleaved_stereo.restype = c_size_t

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 278
if hasattr(_libs['openmpt'], 'openmpt_module_read_interleaved_quad'):
    openmpt_module_read_interleaved_quad = _libs['openmpt'].openmpt_module_read_interleaved_quad
    openmpt_module_read_interleaved_quad.argtypes = [POINTER(openmpt_module), c_int32, c_size_t, POINTER(c_int16)]
    openmpt_module_read_interleaved_quad.restype = c_size_t

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 279
if hasattr(_libs['openmpt'], 'openmpt_module_read_interleaved_float_stereo'):
    openmpt_module_read_interleaved_float_stereo = _libs['openmpt'].openmpt_module_read_interleaved_float_stereo
    openmpt_module_read_interleaved_float_stereo.argtypes = [POINTER(openmpt_module), c_int32, c_size_t, POINTER(c_float)]
    openmpt_module_read_interleaved_float_stereo.restype = c_size_t

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 280
if hasattr(_libs['openmpt'], 'openmpt_module_read_interleaved_float_quad'):
    openmpt_module_read_interleaved_float_quad = _libs['openmpt'].openmpt_module_read_interleaved_float_quad
    openmpt_module_read_interleaved_float_quad.argtypes = [POINTER(openmpt_module), c_int32, c_size_t, POINTER(c_float)]
    openmpt_module_read_interleaved_float_quad.restype = c_size_t

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 282
if hasattr(_libs['openmpt'], 'openmpt_module_get_metadata_keys'):
    openmpt_module_get_metadata_keys = _libs['openmpt'].openmpt_module_get_metadata_keys
    openmpt_module_get_metadata_keys.argtypes = [POINTER(openmpt_module)]
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_module_get_metadata_keys.restype = ReturnString
    else:
        openmpt_module_get_metadata_keys.restype = String
        openmpt_module_get_metadata_keys.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 283
if hasattr(_libs['openmpt'], 'openmpt_module_get_metadata'):
    openmpt_module_get_metadata = _libs['openmpt'].openmpt_module_get_metadata
    openmpt_module_get_metadata.argtypes = [POINTER(openmpt_module), String]
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_module_get_metadata.restype = ReturnString
    else:
        openmpt_module_get_metadata.restype = String
        openmpt_module_get_metadata.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 285
if hasattr(_libs['openmpt'], 'openmpt_module_get_current_speed'):
    openmpt_module_get_current_speed = _libs['openmpt'].openmpt_module_get_current_speed
    openmpt_module_get_current_speed.argtypes = [POINTER(openmpt_module)]
    openmpt_module_get_current_speed.restype = c_int32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 286
if hasattr(_libs['openmpt'], 'openmpt_module_get_current_tempo'):
    openmpt_module_get_current_tempo = _libs['openmpt'].openmpt_module_get_current_tempo
    openmpt_module_get_current_tempo.argtypes = [POINTER(openmpt_module)]
    openmpt_module_get_current_tempo.restype = c_int32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 287
if hasattr(_libs['openmpt'], 'openmpt_module_get_current_order'):
    openmpt_module_get_current_order = _libs['openmpt'].openmpt_module_get_current_order
    openmpt_module_get_current_order.argtypes = [POINTER(openmpt_module)]
    openmpt_module_get_current_order.restype = c_int32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 288
if hasattr(_libs['openmpt'], 'openmpt_module_get_current_pattern'):
    openmpt_module_get_current_pattern = _libs['openmpt'].openmpt_module_get_current_pattern
    openmpt_module_get_current_pattern.argtypes = [POINTER(openmpt_module)]
    openmpt_module_get_current_pattern.restype = c_int32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 289
if hasattr(_libs['openmpt'], 'openmpt_module_get_current_row'):
    openmpt_module_get_current_row = _libs['openmpt'].openmpt_module_get_current_row
    openmpt_module_get_current_row.argtypes = [POINTER(openmpt_module)]
    openmpt_module_get_current_row.restype = c_int32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 290
if hasattr(_libs['openmpt'], 'openmpt_module_get_current_playing_channels'):
    openmpt_module_get_current_playing_channels = _libs['openmpt'].openmpt_module_get_current_playing_channels
    openmpt_module_get_current_playing_channels.argtypes = [POINTER(openmpt_module)]
    openmpt_module_get_current_playing_channels.restype = c_int32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 292
if hasattr(_libs['openmpt'], 'openmpt_module_get_current_channel_vu_mono'):
    openmpt_module_get_current_channel_vu_mono = _libs['openmpt'].openmpt_module_get_current_channel_vu_mono
    openmpt_module_get_current_channel_vu_mono.argtypes = [POINTER(openmpt_module), c_int32]
    openmpt_module_get_current_channel_vu_mono.restype = c_float

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 293
if hasattr(_libs['openmpt'], 'openmpt_module_get_current_channel_vu_left'):
    openmpt_module_get_current_channel_vu_left = _libs['openmpt'].openmpt_module_get_current_channel_vu_left
    openmpt_module_get_current_channel_vu_left.argtypes = [POINTER(openmpt_module), c_int32]
    openmpt_module_get_current_channel_vu_left.restype = c_float

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 294
if hasattr(_libs['openmpt'], 'openmpt_module_get_current_channel_vu_right'):
    openmpt_module_get_current_channel_vu_right = _libs['openmpt'].openmpt_module_get_current_channel_vu_right
    openmpt_module_get_current_channel_vu_right.argtypes = [POINTER(openmpt_module), c_int32]
    openmpt_module_get_current_channel_vu_right.restype = c_float

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 295
if hasattr(_libs['openmpt'], 'openmpt_module_get_current_channel_vu_rear_left'):
    openmpt_module_get_current_channel_vu_rear_left = _libs['openmpt'].openmpt_module_get_current_channel_vu_rear_left
    openmpt_module_get_current_channel_vu_rear_left.argtypes = [POINTER(openmpt_module), c_int32]
    openmpt_module_get_current_channel_vu_rear_left.restype = c_float

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 296
if hasattr(_libs['openmpt'], 'openmpt_module_get_current_channel_vu_rear_right'):
    openmpt_module_get_current_channel_vu_rear_right = _libs['openmpt'].openmpt_module_get_current_channel_vu_rear_right
    openmpt_module_get_current_channel_vu_rear_right.argtypes = [POINTER(openmpt_module), c_int32]
    openmpt_module_get_current_channel_vu_rear_right.restype = c_float

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 298
if hasattr(_libs['openmpt'], 'openmpt_module_get_num_subsongs'):
    openmpt_module_get_num_subsongs = _libs['openmpt'].openmpt_module_get_num_subsongs
    openmpt_module_get_num_subsongs.argtypes = [POINTER(openmpt_module)]
    openmpt_module_get_num_subsongs.restype = c_int32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 299
if hasattr(_libs['openmpt'], 'openmpt_module_get_num_channels'):
    openmpt_module_get_num_channels = _libs['openmpt'].openmpt_module_get_num_channels
    openmpt_module_get_num_channels.argtypes = [POINTER(openmpt_module)]
    openmpt_module_get_num_channels.restype = c_int32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 300
if hasattr(_libs['openmpt'], 'openmpt_module_get_num_orders'):
    openmpt_module_get_num_orders = _libs['openmpt'].openmpt_module_get_num_orders
    openmpt_module_get_num_orders.argtypes = [POINTER(openmpt_module)]
    openmpt_module_get_num_orders.restype = c_int32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 301
if hasattr(_libs['openmpt'], 'openmpt_module_get_num_patterns'):
    openmpt_module_get_num_patterns = _libs['openmpt'].openmpt_module_get_num_patterns
    openmpt_module_get_num_patterns.argtypes = [POINTER(openmpt_module)]
    openmpt_module_get_num_patterns.restype = c_int32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 302
if hasattr(_libs['openmpt'], 'openmpt_module_get_num_instruments'):
    openmpt_module_get_num_instruments = _libs['openmpt'].openmpt_module_get_num_instruments
    openmpt_module_get_num_instruments.argtypes = [POINTER(openmpt_module)]
    openmpt_module_get_num_instruments.restype = c_int32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 303
if hasattr(_libs['openmpt'], 'openmpt_module_get_num_samples'):
    openmpt_module_get_num_samples = _libs['openmpt'].openmpt_module_get_num_samples
    openmpt_module_get_num_samples.argtypes = [POINTER(openmpt_module)]
    openmpt_module_get_num_samples.restype = c_int32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 305
if hasattr(_libs['openmpt'], 'openmpt_module_get_subsong_name'):
    openmpt_module_get_subsong_name = _libs['openmpt'].openmpt_module_get_subsong_name
    openmpt_module_get_subsong_name.argtypes = [POINTER(openmpt_module), c_int32]
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_module_get_subsong_name.restype = ReturnString
    else:
        openmpt_module_get_subsong_name.restype = String
        openmpt_module_get_subsong_name.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 306
if hasattr(_libs['openmpt'], 'openmpt_module_get_channel_name'):
    openmpt_module_get_channel_name = _libs['openmpt'].openmpt_module_get_channel_name
    openmpt_module_get_channel_name.argtypes = [POINTER(openmpt_module), c_int32]
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_module_get_channel_name.restype = ReturnString
    else:
        openmpt_module_get_channel_name.restype = String
        openmpt_module_get_channel_name.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 307
if hasattr(_libs['openmpt'], 'openmpt_module_get_order_name'):
    openmpt_module_get_order_name = _libs['openmpt'].openmpt_module_get_order_name
    openmpt_module_get_order_name.argtypes = [POINTER(openmpt_module), c_int32]
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_module_get_order_name.restype = ReturnString
    else:
        openmpt_module_get_order_name.restype = String
        openmpt_module_get_order_name.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 308
if hasattr(_libs['openmpt'], 'openmpt_module_get_pattern_name'):
    openmpt_module_get_pattern_name = _libs['openmpt'].openmpt_module_get_pattern_name
    openmpt_module_get_pattern_name.argtypes = [POINTER(openmpt_module), c_int32]
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_module_get_pattern_name.restype = ReturnString
    else:
        openmpt_module_get_pattern_name.restype = String
        openmpt_module_get_pattern_name.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 309
if hasattr(_libs['openmpt'], 'openmpt_module_get_instrument_name'):
    openmpt_module_get_instrument_name = _libs['openmpt'].openmpt_module_get_instrument_name
    openmpt_module_get_instrument_name.argtypes = [POINTER(openmpt_module), c_int32]
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_module_get_instrument_name.restype = ReturnString
    else:
        openmpt_module_get_instrument_name.restype = String
        openmpt_module_get_instrument_name.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 310
if hasattr(_libs['openmpt'], 'openmpt_module_get_sample_name'):
    openmpt_module_get_sample_name = _libs['openmpt'].openmpt_module_get_sample_name
    openmpt_module_get_sample_name.argtypes = [POINTER(openmpt_module), c_int32]
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_module_get_sample_name.restype = ReturnString
    else:
        openmpt_module_get_sample_name.restype = String
        openmpt_module_get_sample_name.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 312
if hasattr(_libs['openmpt'], 'openmpt_module_get_order_pattern'):
    openmpt_module_get_order_pattern = _libs['openmpt'].openmpt_module_get_order_pattern
    openmpt_module_get_order_pattern.argtypes = [POINTER(openmpt_module), c_int32]
    openmpt_module_get_order_pattern.restype = c_int32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 313
if hasattr(_libs['openmpt'], 'openmpt_module_get_pattern_num_rows'):
    openmpt_module_get_pattern_num_rows = _libs['openmpt'].openmpt_module_get_pattern_num_rows
    openmpt_module_get_pattern_num_rows.argtypes = [POINTER(openmpt_module), c_int32]
    openmpt_module_get_pattern_num_rows.restype = c_int32

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 315
if hasattr(_libs['openmpt'], 'openmpt_module_get_pattern_row_channel_command'):
    openmpt_module_get_pattern_row_channel_command = _libs['openmpt'].openmpt_module_get_pattern_row_channel_command
    openmpt_module_get_pattern_row_channel_command.argtypes = [POINTER(openmpt_module), c_int32, c_int32, c_int32, c_int]
    openmpt_module_get_pattern_row_channel_command.restype = c_uint8

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 317
if hasattr(_libs['openmpt'], 'openmpt_module_format_pattern_row_channel_command'):
    openmpt_module_format_pattern_row_channel_command = _libs['openmpt'].openmpt_module_format_pattern_row_channel_command
    openmpt_module_format_pattern_row_channel_command.argtypes = [POINTER(openmpt_module), c_int32, c_int32, c_int32, c_int]
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_module_format_pattern_row_channel_command.restype = ReturnString
    else:
        openmpt_module_format_pattern_row_channel_command.restype = String
        openmpt_module_format_pattern_row_channel_command.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 318
if hasattr(_libs['openmpt'], 'openmpt_module_highlight_pattern_row_channel_command'):
    openmpt_module_highlight_pattern_row_channel_command = _libs['openmpt'].openmpt_module_highlight_pattern_row_channel_command
    openmpt_module_highlight_pattern_row_channel_command.argtypes = [POINTER(openmpt_module), c_int32, c_int32, c_int32, c_int]
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_module_highlight_pattern_row_channel_command.restype = ReturnString
    else:
        openmpt_module_highlight_pattern_row_channel_command.restype = String
        openmpt_module_highlight_pattern_row_channel_command.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 320
if hasattr(_libs['openmpt'], 'openmpt_module_format_pattern_row_channel'):
    openmpt_module_format_pattern_row_channel = _libs['openmpt'].openmpt_module_format_pattern_row_channel
    openmpt_module_format_pattern_row_channel.argtypes = [POINTER(openmpt_module), c_int32, c_int32, c_int32, c_size_t, c_int]
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_module_format_pattern_row_channel.restype = ReturnString
    else:
        openmpt_module_format_pattern_row_channel.restype = String
        openmpt_module_format_pattern_row_channel.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 321
if hasattr(_libs['openmpt'], 'openmpt_module_highlight_pattern_row_channel'):
    openmpt_module_highlight_pattern_row_channel = _libs['openmpt'].openmpt_module_highlight_pattern_row_channel
    openmpt_module_highlight_pattern_row_channel.argtypes = [POINTER(openmpt_module), c_int32, c_int32, c_int32, c_size_t, c_int]
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_module_highlight_pattern_row_channel.restype = ReturnString
    else:
        openmpt_module_highlight_pattern_row_channel.restype = String
        openmpt_module_highlight_pattern_row_channel.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 323
if hasattr(_libs['openmpt'], 'openmpt_module_get_ctls'):
    openmpt_module_get_ctls = _libs['openmpt'].openmpt_module_get_ctls
    openmpt_module_get_ctls.argtypes = [POINTER(openmpt_module)]
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_module_get_ctls.restype = ReturnString
    else:
        openmpt_module_get_ctls.restype = String
        openmpt_module_get_ctls.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 324
if hasattr(_libs['openmpt'], 'openmpt_module_ctl_get'):
    openmpt_module_ctl_get = _libs['openmpt'].openmpt_module_ctl_get
    openmpt_module_ctl_get.argtypes = [POINTER(openmpt_module), String]
    if sizeof(c_int) == sizeof(c_void_p):
        openmpt_module_ctl_get.restype = ReturnString
    else:
        openmpt_module_ctl_get.restype = String
        openmpt_module_ctl_get.errcheck = ReturnString

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 325
if hasattr(_libs['openmpt'], 'openmpt_module_ctl_set'):
    openmpt_module_ctl_set = _libs['openmpt'].openmpt_module_ctl_set
    openmpt_module_ctl_set.argtypes = [POINTER(openmpt_module), String, String]
    openmpt_module_ctl_set.restype = c_int

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 90
try:
    OPENMPT_STRING_LIBRARY_VERSION = 'library_version'
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 92
try:
    OPENMPT_STRING_LIBRARY_FEATURES = 'library_features'
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 94
try:
    OPENMPT_STRING_CORE_VERSION = 'core_version'
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 96
try:
    OPENMPT_STRING_BUILD = 'build'
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 98
try:
    OPENMPT_STRING_CREDITS = 'credits'
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 100
try:
    OPENMPT_STRING_CONTACT = 'contact'
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 102
try:
    OPENMPT_STRING_LICENSE = 'license'
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 136
try:
    OPENMPT_STREAM_SEEK_SET = 0
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 137
try:
    OPENMPT_STREAM_SEEK_CUR = 1
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 138
try:
    OPENMPT_STREAM_SEEK_END = 2
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 245
try:
    OPENMPT_MODULE_RENDER_MASTERGAIN_MILLIBEL = 1
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 246
try:
    OPENMPT_MODULE_RENDER_STEREOSEPARATION_PERCENT = 2
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 247
try:
    OPENMPT_MODULE_RENDER_INTERPOLATIONFILTER_LENGTH = 3
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 248
try:
    OPENMPT_MODULE_RENDER_VOLUMERAMPING_STRENGTH = 4
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 250
try:
    OPENMPT_MODULE_COMMAND_NOTE = 0
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 251
try:
    OPENMPT_MODULE_COMMAND_INSTRUMENT = 1
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 252
try:
    OPENMPT_MODULE_COMMAND_VOLUMEEFFECT = 2
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 253
try:
    OPENMPT_MODULE_COMMAND_EFFECT = 3
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 254
try:
    OPENMPT_MODULE_COMMAND_VOLUME = 4
except:
    pass

# /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 255
try:
    OPENMPT_MODULE_COMMAND_PARAMETER = 5
except:
    pass

openmpt_stream_callbacks = struct_openmpt_stream_callbacks # /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 198

openmpt_module = struct_openmpt_module # /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 232

openmpt_module_initial_ctl = struct_openmpt_module_initial_ctl # /home/mrb/Downloads/libopenmpt-0.2.4954/libopenmpt/libopenmpt.h: 237

# No inserted files

