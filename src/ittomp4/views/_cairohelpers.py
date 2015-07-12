# -*- coding: utf-8-unix -*-

import cairo
import contextlib

_cairofont_module = None
_fonts = {}

def cairo_font(name):
    global _cairofont_module, _fonts
    
    if name not in _fonts:
        if _cairofont_module is None:
            from sys import platform as _platform
            if _platform == 'linux' or _platform == 'linux2':
                from ..posix import cairofont
            elif _platform == 'win32':
                from ..windows import cairofont
            elif _platform == 'darwin':
                from ..osx import cairofont

            _cairofont_module = cairofont

        _fonts[name] = _cairofont_module.load_font(name)
        
    return _fonts[name]


@contextlib.contextmanager
def cairo_surface(*image_surface_args):
    surface = cairo.ImageSurface(*image_surface_args)
    yield surface
    del surface

@contextlib.contextmanager
def cairo_context(surface):
    context = cairo.Context(surface)
    yield context
    del context
