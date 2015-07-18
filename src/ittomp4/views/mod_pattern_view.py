# -*- coding: utf-8-unix -*-

import math


from ._cairohelpers import cairo_context, cairo_font

class ModPatternView(object):
    def __init__(self, mod_decoder):
        self.step = 0
        self.mod_decoder = mod_decoder

    def render(self, surface, video_config, state, rect):
        barwidth = 100
        step = 10

        i = self.step
        self.step += 1

        with cairo_context(surface) as ctx:
            ctx.new_path()
            ctx.rectangle(0, 0, video_config.width, video_config.height)
            ctx.set_source_rgb(math.cos(i / 240 * (math.pi * 2)) / 2 + 0.5, 0, math.sin(i / 180 * (math.pi * 2)) / 2 + 0.5)
            ctx.fill()

            horizbar_y_ctr = (video_config.height / 2) + (int(math.cos(i / 240 * (math.pi * 2)) * (video_config.height / 2 * .8)))
            max_extent = int(video_config.height * .08 / 2)

            for h in xrange(max_extent, 0, -1):
                ctx.new_path()
                ctx.rectangle(0, horizbar_y_ctr - h, video_config.width, h * 2)
                ctx.set_source_rgba(1, 1, 1, (max_extent - h) / pow(max_extent, 2))
                ctx.fill()



            ctx.new_path()

            if video_config.width - ((i * step) % video_config.width) < barwidth:
                ctx.rectangle((i * step) % video_config.width - video_config.width, 0, barwidth, video_config.height)
            ctx.rectangle((i * step) % video_config.width, 0, barwidth, video_config.height)

            ctx.set_source_rgb(0.25, 1, 0.25)
            ctx.fill()


            ctx.set_font_face(cairo_font('Comic Sans MS'))
            ctx.set_font_size(128)
            ctx.set_source_rgb(1, 1, 1)

            for pos, ltr in enumerate('  YOU ARE FULL OF BOMBS AND/OR KEYS'):
                x = video_config.width - i * step + (128 * pos)
                y = (video_config.height / 2) - (video_config.height * 0.2 * math.sin((x + (i * step/4)) * math.pi / 1020))

                ctx.move_to(x, y)
                ctx.show_text(ltr)

        surface_data = str(surface.get_data())

        return surface_data
