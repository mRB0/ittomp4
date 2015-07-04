#!/usr/bin/env python
# -*- coding: utf-8-unix -*-

from __future__ import division

import sys
import logging
import contextlib
import math
import struct
import threading
from Queue import Queue, Empty, Full

import cairo
import decode_mod


from sys import platform as _platform
if _platform == 'linux' or _platform == 'linux2':
    import cairofont_freetype as cairofont
elif _platform == 'win32':
    import cairofont_windows as cairofont
elif _platform == 'darwin':
    import cairofont_osx as cairofont

FONT_FACE = cairofont.load_font('Comic Sans MS')


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

class VideoLayout(object):
    def __init__(self, fps):
        self.fps = fps
        self.step = 0

    def build_frame(self):
        barwidth = 100
        step = 10

        i = self.step
        self.step += 1

        with cairo_surface(cairo.FORMAT_ARGB32, 1920, 1080) as surface:
            with cairo_context(surface) as ctx:

                ctx.new_path()
                ctx.rectangle(0, 0, 1920, 1080)
                ctx.set_source_rgb(math.cos(i / 240 * (math.pi * 2)) / 2 + 0.5, 0, math.sin(i / 180 * (math.pi * 2)) / 2 + 0.5)
                ctx.fill()

                horizbar_y_ctr = (1080 / 2) + (int(math.cos(i / 240 * (math.pi * 2)) * (1080 / 2 * .8)))
                max_extent = int(1080 * .08 / 2)

                for h in xrange(max_extent, 0, -1):
                    ctx.new_path()
                    ctx.rectangle(0, horizbar_y_ctr - h, 1920, h * 2)
                    ctx.set_source_rgba(1, 1, 1, (max_extent - h) / pow(max_extent, 2))
                    ctx.fill()



                ctx.new_path()

                if 1920 - ((i * step) % 1920) < barwidth:
                    ctx.rectangle((i * step) % 1920 - 1920, 0, barwidth, 1080)
                ctx.rectangle((i * step) % 1920, 0, barwidth, 1080)

                ctx.set_source_rgb(0.25, 1, 0.25)
                ctx.fill()


                ctx.set_font_face(FONT_FACE)
                ctx.set_font_size(128)
                ctx.set_source_rgb(1, 1, 1)

                for pos, ltr in enumerate('  YOU ARE FULL OF BOMBS AND/OR KEYS'):
                    x = 1920 - i * step + (128 * pos)
                    y = (1080 / 2) - (1080 * 0.2 * math.sin((x + (i * step/4)) * math.pi / 1020))

                    ctx.move_to(x, y)
                    ctx.show_text(ltr)

            surface_data = str(surface.get_data())

            return surface_data

class ModDecoder(object):

    def __init__(self, mod_filename):
        self.fps = 48000
        self._filename = mod_filename
        self.module = decode_mod.Module(self._filename)

    def close(self):
        if self.module is not None:
            self.module.close()
            self.module = None
        
    def get_frames(self, count):
        samples_buffer_raw = self.module.decode(count)
        if samples_buffer_raw is None:
            return None
        samples_buffer = ''.join([struct.pack('<h', samp) for samp in samples_buffer_raw])

        return samples_buffer
        
    def get_pattern_state(self):
        pass

class SynchronizerDone(object): pass
class SynchronizerAbort(object): pass

class Synchronizer(object):
    DONE = SynchronizerDone()
    ABORT = SynchronizerAbort()
    
    def __init__(self, audio_decoder, video_layout):
        self._audio_decoder = audio_decoder
        self._video_layout = video_layout
        
        self._video_frames_per_second = video_layout.fps
        self._audio_frames_per_second = audio_decoder.fps
        self._audio_frames_per_video_frame = self._audio_frames_per_second / self._video_frames_per_second
        
        self._video_frames_produced = 0
        self._audio_frames_produced = 0

        self._video_queue = Queue()
        self._audio_queue = Queue()

        self._abortLock = threading.Condition()
        self._abort = False
        self._running = False
        
    def frames_from_queue(self, q):
        exit_reason = Synchronizer.ABORT

        try:
            while True:
                logging.debug("Fetch a frame")
                frame_data = q.get()
                with self._abortLock:
                    self._abortLock.notify()

                if frame_data is Synchronizer.DONE:
                    exit_reason = Synchronizer.DONE
                    break
                elif frame_data is Synchronizer.ABORT:
                    logging.warning("Frame delivery aborted")
                    break
                yield frame_data
        finally:
            yield exit_reason
        

    def _audio_frames_to_next_video_frame(self):
        overshoot = self._audio_frames_produced % self._audio_frames_per_video_frame
        return int(math.ceil(self._audio_frames_per_video_frame - overshoot))
        
    
    def _run(self):
        exit_reason = None
        try:
            while True:
                with self._abortLock:
                    while self._video_queue.qsize() > 0 and not self._abort:
                        self._abortLock.wait()
                        
                    if self._abort:
                        logging.warning("Received abort request")
                        exit_reason = Synchronizer.ABORT
                        self._running = False
                        break
                    
                    logging.debug("Produce frame: audio queue size = {}, video queue size = {}".format(self._audio_queue.qsize(), self._video_queue.qsize()))

                    audio_frame_count = self._audio_frames_to_next_video_frame()
                    logging.debug("Produce {} audio frames".format(audio_frame_count))

                    audio_frames = self._audio_decoder.get_frames(audio_frame_count)
                    if audio_frames is None:
                        exit_reason = Synchronizer.DONE
                        self._running = False
                        break

                    # TODO: do this only if supported by audio decoder
                    pattern_state = self._audio_decoder.get_pattern_state()

                    video_frame = self._video_layout.build_frame() # TODO: pass pattern state, vu state, etc.
                    self._audio_queue.put(audio_frames)
                    self._video_queue.put(video_frame)
            
        finally:
            self._video_queue.put(exit_reason)
            self._audio_queue.put(exit_reason)

    def start(self):
        self._running = True
        self._abort = False
        
        self._thread = threading.Thread(target=self._run, name="synchronizer")
        self._thread.daemon = True
        self._thread.start()

    def abort(self):
        logging.debug("Request abort")
        with self._abortLock:
            if self._running:
                logging.debug("Drain frame queues")
                try:
                    while True:
                        self._audio_queue.get(False)
                except Empty:
                    pass
                try:
                    while True:
                        self._video_queue.get(False)
                except Empty:
                    pass

                self._abort = True
                self._abortLock.notify()

class VideoSource(object):
    def __init__(self, synchronizer):
        self._synchronizer = synchronizer

    def frames(self):
        for f in self._synchronizer.frames_from_queue(self._synchronizer._video_queue):
            yield f

    def abort(self):
        self._synchronizer.abort()

    
class AudioSource(object):
    def __init__(self, synchronizer):
        self._synchronizer = synchronizer

    def frames(self):
        for f in self._synchronizer.frames_from_queue(self._synchronizer._audio_queue):
            yield f

    def abort(self):
        self._synchronizer.abort()

            
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(threadName)s %(levelname)-7s %(message)s")

    import videofeeder

    synchronizer = Synchronizer(ModDecoder(sys.argv[1]), VideoLayout(60))
    audio_source = AudioSource(synchronizer)
    video_source = VideoSource(synchronizer)

    synchronizer.start()
    
    videofeeder.Encoder(audio_source, video_source).run()

