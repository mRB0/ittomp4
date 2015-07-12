#!/usr/bin/env python
# -*- coding: utf-8-unix -*-

from contextlib import contextmanager

import ctypes
import ctypes.util
from ctypes import CFUNCTYPE

import cairo

objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('objc'))
Foundation = ctypes.CDLL(ctypes.util.find_library('Foundation'))
CoreText = ctypes.CDLL(ctypes.util.find_library('CoreText'))


CFTypeRef = ctypes.c_void_p
CFIndex = ctypes.c_long
CFStringEncoding = ctypes.c_uint32
Boolean = ctypes.c_uint8
kCFStringEncodingUTF8 = 0x08000100
CGFontRef = CFTypeRef
CFStringRef = CFTypeRef

class CFRange(ctypes.Structure):
    _fields_ = [('location', CFIndex),
                ('length', CFIndex)]


CFStringGetBytes = CFUNCTYPE(CFIndex, CFStringRef, CFRange, CFStringEncoding, ctypes.c_char, ctypes.c_uint8, ctypes.POINTER(ctypes.c_char), CFIndex, ctypes.POINTER(CFIndex))(('CFStringGetBytes', Foundation))
CFStringGetLength = CFUNCTYPE(CFIndex, CFStringRef)(('CFStringGetLength', Foundation))
CFStringCreateWithBytes = CFUNCTYPE(CFStringRef, ctypes.c_void_p, ctypes.POINTER(ctypes.c_char), CFIndex, CFStringEncoding, Boolean)(('CFStringCreateWithBytes', Foundation))
CFRelease = CFUNCTYPE(None, CFTypeRef)(('CFRelease', Foundation))

CGFontCreateWithFontName = CFUNCTYPE(CGFontRef, CFStringRef)(('CGFontCreateWithFontName', CoreText))
CGFontGetXHeight = CFUNCTYPE(ctypes.c_int32, CGFontRef)(('CGFontGetXHeight', CoreText))
CGFontGetUnitsPerEm = CFUNCTYPE(ctypes.c_int32, CGFontRef)(('CGFontGetUnitsPerEm', CoreText))
CGFontGetNumberOfGlyphs = CFUNCTYPE(ctypes.c_int32, CGFontRef)(('CGFontGetNumberOfGlyphs', CoreText))
CGFontCopyFullName = CFUNCTYPE(CFStringRef, CGFontRef)(('CGFontCopyFullName', CoreText))

def decodeCFString(stringRef):
    length = CFStringGetBytes(stringRef,
                              CFRange(0, CFStringGetLength(stringRef)),
                              kCFStringEncodingUTF8,
                              '?',
                              0,
                              None,
                              0,
                              None)

    stringBuf = (ctypes.c_char * length)()
    CFStringGetBytes(stringRef,
                     CFRange(0, CFStringGetLength(stringRef)),
                     kCFStringEncodingUTF8,
                     '?',
                     0,
                     stringBuf,
                     length,
                     None)

    return ''.join(stringBuf).decode('utf-8')

def createCFString(unistring):
    s = unistring.encode('utf-8') if isinstance(unistring, unicode) else unistring
    length = len(s)
    bytesArray = (ctypes.c_char * length)(*list(s))

    return CFStringCreateWithBytes(None, bytesArray, length, kCFStringEncodingUTF8, False)


@contextmanager
def autoreleasepool():
    objc.objc_getClass.restype = ctypes.c_void_p
    objc.sel_registerName.restype = ctypes.c_void_p
    objc.objc_msgSend.restype = ctypes.c_void_p
    objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

    NSAutoreleasePool = objc.objc_getClass('NSAutoreleasePool')
    pool = objc.objc_msgSend(NSAutoreleasePool, objc.sel_registerName('alloc'))
    pool = objc.objc_msgSend(pool, objc.sel_registerName('init'))

    yield

    objc.objc_msgSend(pool, objc.sel_registerName('drain'))

def create_cgfontref(font_name):
    with autoreleasepool():

        cf_font_name = createCFString(font_name)
        font_ref = CGFontCreateWithFontName(cf_font_name)
        CFRelease(cf_font_name)

        if not font_ref:
            raise LookupError("Font named {!r} not found".format(font_name))

        return font_ref


PycairoContext = None
def create_cairo_font_face_for_font_named(font_name, faceindex=0, loadoptions=0):
    global _freetype_so
    global _cairo_so
    global _ft_lib
    global _surface
    global PycairoContext

    CAIRO_STATUS_SUCCESS = 0
    
    font = create_cgfontref(font_name)

    if PycairoContext is None:

        # find shared objects
        _cairo_so = ctypes.CDLL(ctypes.util.find_library('cairo'))

        _cairo_so.cairo_quartz_font_face_create_for_cgfont.restype = ctypes.c_void_p
        _cairo_so.cairo_quartz_font_face_create_for_cgfont.argtypes = [ CGFontRef ]
        _cairo_so.cairo_set_font_face.argtypes = [ ctypes.c_void_p, ctypes.c_void_p ]
        _cairo_so.cairo_font_face_status.argtypes = [ ctypes.c_void_p ]
        _cairo_so.cairo_status.argtypes = [ ctypes.c_void_p ]

        class _PycairoContext(ctypes.Structure):
            _fields_ = [("PyObject_HEAD", ctypes.c_byte * object.__basicsize__),
                ("ctx", ctypes.c_void_p),
                ("base", ctypes.c_void_p)]

        PycairoContext = _PycairoContext

    _surface = cairo.ImageSurface (cairo.FORMAT_A8, 0, 0)
    # create freetype face
    cairo_ctx = cairo.Context (_surface)
    cairo_t = PycairoContext.from_address(id(cairo_ctx)).ctx

    # create cairo font face for freetype face
    cr_face = _cairo_so.cairo_quartz_font_face_create_for_cgfont(font)
    if CAIRO_STATUS_SUCCESS != _cairo_so.cairo_font_face_status (cr_face):
        raise Exception("Error creating cairo font face for " + filename)

    _cairo_so.cairo_set_font_face (cairo_t, cr_face)
    if CAIRO_STATUS_SUCCESS != _cairo_so.cairo_status (cairo_t):
        raise Exception("Error creating cairo font face for " + filename)

    face = cairo_ctx.get_font_face ()

    CFRelease(font)
    
    return face

def load_font(font_name):
    return create_cairo_font_face_for_font_named(font_name)

if __name__ == '__main__':
    import sys
    font_ref = create_cgfontref(sys.argv[1])

    cf_font_name = CGFontCopyFullName(font_ref)
    print decodeCFString(cf_font_name)
    CFRelease(cf_font_name)

    print "Glyphs: {}".format(CGFontGetNumberOfGlyphs(font_ref))

    CFRelease(font_ref)
    
