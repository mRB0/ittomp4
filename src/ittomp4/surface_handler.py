# -*- coding: utf-8-unix -*-

from __future__ import division, absolute_import

import cairo

from .views._cairohelpers import cairo_surface

class SurfaceHandler(object):
    def __init__(self, video_config, root_view):
        self.video_config = video_config
        self.root_view = root_view

    def render(self, decode_state):
        with cairo_surface(cairo.FORMAT_ARGB32, self.video_config.width, self.video_config.height) as surface:
            return self.root_view.render(surface, self.video_config, decode_state)
            
