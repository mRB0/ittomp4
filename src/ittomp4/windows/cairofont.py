# -*- coding: utf-8-unix -*-

# Adapted from http://pyglet.googlecode.com/hg-history/8cca88b20854040d828cae96cf7d69d2415880eb/pyglet/font/win32query.py

"""
Query system Windows fonts with pure Python.

Public domain work by anatoly techtonik <techtonik@gmail.com>
Use MIT License if public domain doesn't make sense for you.



The task: Get monospace font for an application in the order of
preference.

The problem: Font ID in Windows is its name. Windows doesn't provide
any information about filenames they contained in. From two different
files with the same font name you'll can get only one.

Windows also doesn't have a clear concept of _generic font family_
familiar from CSS specification. Here is how fontquery maps Windows
LOGFONT properties to generic CSS font families:

  serif      -   (LOGFONT.lfPitchAndFamily >> 4) == FF_ROMAN
  sans-serif -   (LOGFONT.lfPitchAndFamily >> 4) == FF_SWISS
  cursive    -   (LOGFONT.lfPitchAndFamily >> 4) == FF_SCRIPT
  fantasy    -   (LOGFONT.lfPitchAndFamily >> 4) == FF_DECORATIVE
  monospace  -   (LOGFONT.lfPitchAndFamily >> 4) == FF_MODERN

NOTE: Raster 'Modern' font and OpenType 'OCR A Extended' are
      FF_MODERN, but have VARIABLE_PITCH for some reason

      [ ] find a way to check char's pitch matches manually


Use cases:
 [x] get the list of all available system font names
 [ ] get the list of all fonts for generic family
 [ ] get the list of all fonts for specific charset
 [ ] check if specific font is available

Considerations:
 - performance of querying all system fonts is not measured
 - Windows doesn't allow to get filenames of the fonts, so if there
   are two fonts with the same name, one will be missing

MSDN:

    If you request a font named Palatino, but no such font is available
on the system, the font mapper will substitute a font that has similar
attributes but a different name.

   [ ] check if font chosen by the system has required family

    To get the appropriate font, call EnumFontFamiliesEx with the
desired font characteristics in the LOGFONT structure, then retrieve the
appropriate typeface name and create the font using CreateFont or
CreateFontIndirect.

"""
DEBUG = False

__all__ = ['have_font', 'font_list']

__version__ = '0.1'
__url__ = 'https://bitbucket.org/techtonik/fontquery'


#-- CHAPTER 1: GET ALL SYSTEM FONTS USING EnumFontFamiliesEx FROM GDI --

"""
Q: Why GDI? Why not GDI+? 
A: Wikipedia:

    Because of the additional text processing and resolution independence
capabilities in GDI+, text rendering is performed by the CPU [2] and it
is nearly an order of magnitude slower than in hardware accelerated GDI.[3]
Chris Jackson published some tests indicating that a piece of text
rendering code he had written could render 99,000 glyphs per second in GDI,
but the same code using GDI+ rendered 16,600 glyphs per second.
"""

import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# --- define necessary data structures from wingdi.h

# for calling ANSI functions of Windows API (end with A) TCHAR is
# defined as single char, for Unicode ones (end witn W) it is WCHAR
CHAR = ctypes.c_wchar    # Python 2.7 compatibility
TCHAR = CHAR
BYTE = ctypes.c_ubyte   # http://bugs.python.org/issue16376

# charset codes for LOGFONT structure
ANSI_CHARSET    = 0
ARABIC_CHARSET  = 178
BALTIC_CHARSET  = 186
CHINESEBIG5_CHARSET = 136
DEFAULT_CHARSET = 1
  # - charset for current system locale -
  #   means function can be called several times
  #   for the single font (for each charset)
EASTEUROPE_CHARSET = 238
GB2312_CHARSET = 134
GREEK_CHARSET  = 161
HANGUL_CHARSET = 129
HEBREW_CHARSET = 177
JOHAB_CHARSET  = 130
MAC_CHARSET = 77
OEM_CHARSET = 255  # OS dependent system charset
RUSSIAN_CHARSET  = 204
SHIFTJIS_CHARSET = 128
SYMBOL_CHARSET   = 2
THAI_CHARSET     = 222
TURKISH_CHARSET  = 162
VIETNAMESE_CHARSET = 163

# build lookup dictionary to get charset name from its code
CHARSET_NAMES = {}
for (name, value) in locals().copy().items():
  if name.endswith('_CHARSET'):
    CHARSET_NAMES[value] = name

# font pitch constants ('fixed pitch' means 'monospace')
FIXED_PITCH = 1
VARIABLE_PITCH = 2

# Windows font family constants
FF_ROMAN = 1      # with serifs, proportional
FF_SWISS = 2      # w/out serifs, proportional
FF_MODERN = 3     # constant stroke width
FF_SCRIPT = 4     # handwritten
FF_DECORATIVE = 5 # novelty


class LOGFONT(ctypes.Structure):
  # EnumFontFamiliesEx examines only 3 fields:
  #  - lfCharSet
  #  - lfFaceName  - empty string enumerates one font in each available
  #                  typeface name, valid typeface name gets all fonts
  #                  with that name
  #  - lfPitchAndFamily - must be set to 0 [ ]
  _fields_ = [
    ('lfHeight', wintypes.LONG),
      # value > 0  specifies the largest size of *char cell* to match
      #            char cell = char height + internal leading
      # value = 0  makes matched use default height for search
      # value < 0  specifies the largest size of *char height* to match
    ('lfWidth',  wintypes.LONG),
      # average width also in *logical units*, which are pixels in
      # default _mapping mode_ (MM_TEXT) for device
    ('lfEscapement',  wintypes.LONG),
      # string baseline rotation in tenths of degrees
    ('lfOrientation', wintypes.LONG),
      # character rotation in tenths of degrees
    ('lfWeight', wintypes.LONG),
      # 0 through 1000  400 is normal, 700 is bold, 0 is default
    ('lfItalic', BYTE),
    ('lfUnderline', BYTE),
    ('lfStrikeOut', BYTE),
    ('lfCharSet',   BYTE),
      # ANSI_CHARSET, BALTIC_CHARSET, ... - see *_CHARSET constants above
    ('lfOutPrecision', BYTE),
      # many constants how the output must match height, width, pitch etc.
      # OUT_DEFAULT_PRECIS
      # [ ] TODO
    ('lfClipPrecision', BYTE),
      # how to clip characters, no useful properties, leave default value
      # CLIP_DEFAULT_PRECIS
    ('lfQuality', BYTE),
      # ANTIALIASED_QUALITY
      # CLEARTYPE_QUALITY
      # DEFAULT_QUALITY 
      # DRAFT_QUALITY
      # NONANTIALIASED_QUALITY
      # PROOF_QUALITY
    ('lfPitchAndFamily', BYTE),
      # DEFAULT_PITCH
      # FIXED_PITCH
      # VARIABLE_PITCH
      #    stacked with any of 
      # FF_DECORATIVE   - novelty
      # FF_DONTCARE     - default font
      # FF_MODERN       - monospace
      # FF_ROMAN        - proportional (variable char width) with serifs
      # FF_SCRIPT       - handwritten
      # FF_SWISS        - proportional without serifs
    ('lfFaceName', TCHAR*32)]
      # typeface name of the font - null-terminated string

class FONTSIGNATURE(ctypes.Structure):
  # supported code pages and Unicode subranges for the font
  # needed for NEWTEXTMETRICEX structure
  _fields_ = [
    ('sUsb', wintypes.DWORD*4),  # 128-bit Unicode subset bitfield (USB)
    ('sCsb', wintypes.DWORD*2)]  # 64-bit, code-page bitfield (CPB)

class NEWTEXTMETRIC(ctypes.Structure):
  # physical font attributes for True Type fonts
  # needed for NEWTEXTMETRICEX structure
  _fields_ = [
    ('tmHeight', wintypes.LONG),
    ('tmAscent', wintypes.LONG),
    ('tmDescent', wintypes.LONG),
    ('tmInternalLeading', wintypes.LONG),
    ('tmExternalLeading', wintypes.LONG),
    ('tmAveCharWidth', wintypes.LONG),
    ('tmMaxCharWidth', wintypes.LONG),
    ('tmWeight', wintypes.LONG),
    ('tmOverhang', wintypes.LONG),
    ('tmDigitizedAspectX', wintypes.LONG),
    ('tmDigitizedAspectY', wintypes.LONG),
    ('mFirstChar', TCHAR),
    ('mLastChar', TCHAR),
    ('mDefaultChar', TCHAR),
    ('mBreakChar', TCHAR),
    ('tmItalic', BYTE),
    ('tmUnderlined', BYTE),
    ('tmStruckOut', BYTE),
    ('tmPitchAndFamily', BYTE),
    ('tmCharSet', BYTE),
    ('tmFlags', wintypes.DWORD),
    ('ntmSizeEM', wintypes.UINT),
    ('ntmCellHeight', wintypes.UINT),
    ('ntmAvgWidth', wintypes.UINT)]

class NEWTEXTMETRICEX(ctypes.Structure):
  # physical font attributes for True Type fonts
  # needed for FONTENUMPROC callback function
  _fields_ = [
    ('ntmTm', NEWTEXTMETRIC),
    ('ntmFontSig', FONTSIGNATURE)]


# type for a function that is called by the system for
# each font during execution of EnumFontFamiliesEx
FONTENUMPROC = ctypes.WINFUNCTYPE(
  ctypes.c_int,  # return non-0 to continue enumeration, 0 to stop
  ctypes.POINTER(LOGFONT), 
  ctypes.POINTER(NEWTEXTMETRICEX),
  wintypes.DWORD,  # font type, a combination of
                   #   DEVICE_FONTTYPE
                   #   RASTER_FONTTYPE 
                   #   TRUETYPE_FONTTYPE 
  wintypes.LPARAM
)

_font_names = set()
def _enum_font_names(logfont, textmetricex, fonttype, param):
  """callback function to be executed during EnumFontFamiliesEx
     call for each font name. it stores names in global variable
  """
  global _font_names
  lf = logfont.contents
  _font_names.add(lf.lfFaceName)

  if DEBUG:
    info = ''
 
    pitch = lf.lfPitchAndFamily & 0b11
    if pitch == FIXED_PITCH:
      info += 'FP '
    elif pitch == VARIABLE_PITCH: 
      info += 'VP '
    else:
      info += '   '

    family = lf.lfPitchAndFamily >> 4
    if family == FF_MODERN:
      info += 'M  '
    else:
      info += 'NM '

    style = [' ']*3
    if lf.lfItalic:
      style[0] = 'I'
    if lf.lfUnderline:
      style[1] = 'U'
    if lf.lfStrikeOut:
      style[2] = 'S'
    info += ''.join(style)

    info += ' %s' % lf.lfWeight

    #if pitch == FIXED_PITCH:
    if 1:
      print('%s CHARSET: %3s  %s' % (info, lf.lfCharSet, lf.lfFaceName))

  return 1   # non-0 to continue enumeration
enum_font_names = FONTENUMPROC(_enum_font_names)

# --- /define


import sys
PY3K = sys.version_info >= (3, 0)


# --- prepare and call EnumFontFamiliesEx

def query(charset=DEFAULT_CHARSET):
  """
  Prepare and call EnumFontFamiliesEx.

  query()
    - return sorted list of all available system fonts
  query(charset=ANSI_CHARSET)
    - return sorted list of system fonts supporting ANSI charset

  """
  global _font_names

  # 1. Get device context of the entire screen
  hdc = user32.GetDC(None)

  # 2. Call EnumFontFamiliesExA (ANSI version)

  # 2a. Call with empty font name to query all available fonts
  #     (or fonts for the specified charset)
  #
  # NOTES:
  #
  #  * there are fonts that don't support ANSI charset
  #  * for DEFAULT_CHARSET font is passed to callback function as
  #    many times as charsets it supports

  # [ ] font name should be less than 32 symbols with terminating \0
  # [ ] check double purpose - enumerate all available font names
  #      - enumerate all available charsets for a single font
  #      - other params?

  logfont = LOGFONT(0, 0, 0, 0, 0, 0, 0, 0, charset,
                    0, 0, 0, 0, u'')
  _font_names = set()  # clear _font_names for enum_font_names callback
  res = gdi32.EnumFontFamiliesExW(
          hdc,   # handle to device context
          ctypes.byref(logfont),
          enum_font_names, # pointer to callback function
          0,  # lParam  - application-supplied data
          0)  # dwFlags - reserved = 0
  # res here is the last value returned by callback function

  # 3. Release DC
  user32.ReleaseDC(None, hdc)

  if PY3K: # convert to strings from bytes
    return [name.decode('utf-8') for name in sorted(_font_names)]
  else:
    return sorted(_font_names)


# --- Public API ---

def have_font(name):
  """Return True if font with specified name is present."""
  if name in query():
    return True
  else:
    return False

def font_list():
  """Return list of system installed font names."""
  return query()

def get_logfont_named(font_name):
    return LOGFONT(0, 0, 0, 0, 0, 0, 0, 0, DEFAULT_CHARSET,
                   0, 0, 4, 0, font_name) # 4 = antialias

import cairo

PycairoContext = None
def get_cairo_font(font_name, faceindex=0, loadoptions=0):
    global _cairo_so
    global _surface
    global PycairoContext

    CAIRO_STATUS_SUCCESS = 0
    FT_Err_Ok = 0

    if PycairoContext is None:

        # find shared objects
        _cairo_so = ctypes.CDLL (r"c:\Python27\Lib\site-packages\cairo\_cairo.pyd")

        _cairo_so.cairo_win32_font_face_create_for_logfontw.restype = ctypes.c_void_p
        _cairo_so.cairo_win32_font_face_create_for_logfontw.argtypes = [ ctypes.POINTER(LOGFONT) ]
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
    cr_face = _cairo_so.cairo_win32_font_face_create_for_logfontw(ctypes.pointer(get_logfont_named(font_name)))
    if CAIRO_STATUS_SUCCESS != _cairo_so.cairo_font_face_status (cr_face):
        raise Exception("Error creating cairo font face for " + filename)

    _cairo_so.cairo_set_font_face (cairo_t, cr_face)
    if CAIRO_STATUS_SUCCESS != _cairo_so.cairo_status (cairo_t):
        raise Exception("Error creating cairo font face for " + filename)

    face = cairo_ctx.get_font_face ()

    return face

def load_font(font_name):
    return get_cairo_font(font_name)



if __name__ == '__main__':
  for f in font_list():
    print(f)
  if DEBUG:
    print("Total: %s" % len(font_list()))

  if DEBUG:
    print('Have font "Arial"? %s' % have_font('Arial'))
    print('Have font "missing-one"? %s' % have_font('missing-one'))

