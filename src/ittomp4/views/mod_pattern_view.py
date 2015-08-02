# -*- coding: utf-8-unix -*-

from __future__ import division

import math

import logging as _logging
logger = _logging.getLogger(__name__)

# - Module context -

class ModContext(object):
    def __init__(self):
        pass

# - The actual view -

from ._cairohelpers import cairo_context, cairo_font

COLUMN_COLORS = {'.': (0.4, 0.4, 0.4),
                 'n': (1.0, 1.0, 1.0),
                 'i': (0.0, 0.8, 1.0),
                 'v': (0.4, 1.0, 0.2),
                 'u': (0.2, 0.5, 0.1),
                 'f': (1.0, 0.1, 0.2),
                 'e': (0.7, 0.0, 0.1)}

class ModPatternView(object):
    def __init__(self, decoder):
        self.step = 0
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
            ctx.rectangle(0, 0, rect.size.w, rect.size.h)
            ctx.set_source_rgb(0.06, 0.06, 0.06)
            ctx.fill()
            
            ctx.set_font_face(cairo_font('Consolas'))
            ctx.set_font_size(18)

            font_ascent, font_descent, font_height, font_max_x_advance, font_max_y_advance = ctx.font_extents()

            text_x_bearing, text_y_bearing, text_width, text_height, text_x_advance, text_y_advance = ctx.text_extents('m')

            # highlight the current cow (center)
            y_ctr = h / 2
            ctx.new_path()
            ctx.rectangle(0, y_ctr - font_height / 2, w, font_height)
            ctx.set_source_rgb(0, 0.16, 0.24)
            ctx.fill()

            # figure out how much space to leave for things
            pattern_index = self.decoder.get_current_pattern()
            row_index = self.decoder.get_current_row()
            formatted_rows = self.decoder.get_formatted_pattern_data(pattern_index)

            y_ctr_baseline = y_ctr + font_height / 2 - font_descent
            y_top_row = y_ctr_baseline - (row_index * font_height)

            # every channel really should be the same width, but we do this anyway for safety
            # (although we should be able to support a different width per-channel, and can calculate a max width unique to each channel)
            # (this won't happen for mods or ITs or anything though)
            channel_max_width = max(max(len(chan[0]) for chan in formatted_chans) for formatted_chans in formatted_rows) * text_width
            channel_count = max(len(formatted_chans) for formatted_chans in formatted_rows)

            # draw vertical spacers between channels
            ctx.set_source_rgb(0, 0.24, 0.36)
            spacer_width = text_width / 2
            ptn_top = y_ctr - (font_height / 2) - (row_index * font_height)
            ptn_bottom = ptn_top + (len(formatted_rows) * font_height)

            row_display_width = text_width * 3
            channels_left = row_display_width + spacer_width
            
            for channel_index in xrange(channel_count):
                x_offset = channels_left - spacer_width + (channel_index * (channel_max_width + spacer_width))
                ctx.new_path()
                ctx.rectangle(x_offset + (spacer_width / 2) - (spacer_width / 4),
                              max(ptn_top, 0),
                              spacer_width / 2,
                              min(ptn_bottom, h))
                ctx.fill()

            
            # draw some note data!
            for row, formatted_channels in enumerate(formatted_rows):
                y_row = y_top_row + (row * font_height)

                ctx.set_source_rgb(0.6, 1.0, 0.6)
                row_index_text = '{:03d}'.format(row)[-3:]
                for i, letter in enumerate(row_index_text):
                    ctx.move_to(i * text_width, y_row)
                    ctx.show_text(letter)
                    
                
                for chan, formatted_channel in enumerate(formatted_channels):
                    x_channel = channels_left + chan * (channel_max_width + spacer_width)
                    
                    for i, (letter, highlight) in enumerate(zip(*formatted_channel)):
                        ctx.set_source_rgb(*COLUMN_COLORS.get(highlight, (1, 1, 1)))
                        
                        x_letter = x_channel + (i * text_width)
                        ctx.move_to(x_letter, y_row)
                        ctx.show_text(letter)
            
            #ctx.move_to(0, y_ctr_baseline)
            #ctx.show_text("some text in the top-left")

            ctx.restore()
            
        surface_data = str(surface.get_data())

        return surface_data
