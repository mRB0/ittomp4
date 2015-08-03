# -*- coding: utf-8-unix -*-

from __future__ import division

import math

import logging as _logging
logger = _logging.getLogger(__name__)

from ._cairohelpers import cairo_context, cairo_font

COLUMN_COLORS = {'.': (0.4, 0.4, 0.4),
                 'n': (1.0, 1.0, 1.0),
                 'i': (0.0, 0.8, 1.0),
                 'v': (0.4, 1.0, 0.2),
                 'u': (0.2, 0.5, 0.1),
                 'f': (1.0, 0.1, 0.2),
                 'e': (0.7, 0.0, 0.1)}

class ModHeaderView(object):
    def __init__(self, decoder):
        self.decoder = decoder

    def render(self, surface, video_config, state, rect):
        with cairo_context(surface) as ctx:
            ctx.save()
            
            ctx.new_path()
            ctx.rectangle(rect.origin.x, rect.origin.y, rect.size.w, rect.size.h)
            ctx.clip()

            # originate our drawing at 0, 0
            ctx.translate(rect.origin.x, rect.origin.y)

            w, h = rect.size.w, rect.size.h

            ctx.new_path()
            ctx.rectangle(0, 0, w, h)
            ctx.set_source_rgb(0.3, 0.00, 0.00)
            ctx.fill()
            
            ctx.set_font_face(cairo_font('Consolas'))
            ctx.set_font_size(16)

            font_ascent, font_descent, font_height, font_max_x_advance, font_max_y_advance = ctx.font_extents()
            
            
            y_ctr = h / 2
            y_ctr_baseline = y_ctr + font_height / 2 - font_descent

            ctx.set_source_rgb(1, 1, 1)
            infoline = '{} {:03d}/{:03d}'.format(self.decoder.get_title(),
                                                 self.decoder.get_current_order(),
                                                 self.decoder.get_order_count() - 1)
            
            text_x_bearing, text_y_bearing, text_width, text_height, text_x_advance, text_y_advance = ctx.text_extents(infoline)

            ctx.move_to(w / 2 - text_width / 2, y_ctr_baseline)
            ctx.show_text(infoline)
