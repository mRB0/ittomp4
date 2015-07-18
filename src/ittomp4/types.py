# -*- coding: utf-8-unix -*-

from __future__ import division, absolute_import

from collections import namedtuple

VideoConfig = namedtuple('VideoConfig', ('width', 'height', 'fps'))
AudioConfig = namedtuple('AudioConfig', ('fps'))

Config = namedtuple('Config', ('video', 'audio'))

Point = namedtuple('Point', ('x', 'y'))
Size = namedtuple('Size', ('w', 'h'))
Rect = namedtuple('Rect', ('origin', 'size'))

def makerect(x, y, w, h):
    return Rect(Point(x, y), Size(w, h))
