# -*- coding: utf-8-unix -*-

from __future__ import division

from collections import namedtuple

import logging as _logging
logger = _logging.getLogger(__name__)

PositionedView = namedtuple('PositionedView', ('view', 'rect'))

class Framer(object):
    def __init__(self):
        self.views = []

    def add(self, view, rect):
        self.views.append(PositionedView(view, rect))

    def render(self, surface, video_config, state, rect):
        for view, viewrect in self.views:
            view.render(surface, video_config, state, viewrect)
    
