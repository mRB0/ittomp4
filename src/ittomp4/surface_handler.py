# -*- coding: utf-8-unix -*-

from collections import namedtuple

import cairo

from .views._cairohelpers import cairo_surface

VideoConfig = namedtuple('VideoConfig', ('width', 'height', 'fps'))

class SurfaceHandler(object):
    def __init__(self, video_config, root_view):
        self.video_config = video_config
        self.root_view = root_view

    def render(self, decode_state):
        with cairo_surface(cairo.FORMAT_ARGB32, 1920, 1080) as surface:
            return self.root_view.render(surface, self.video_config, decode_state)
            
