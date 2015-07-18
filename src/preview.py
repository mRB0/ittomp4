# -*- coding: utf-8-unix -*-

from __future__ import division

from multiprocessing import Queue, Process
from Queue import Empty

import Tkinter
from cStringIO import StringIO
import logging as _logging
from itertools import izip


logger = _logging.getLogger(__name__)

_STOP = "stop"

class Image(object):
    def __init__(self, data):
        self.data = data

class Preview(object):
    
    def _ui_thread(self):
        _logging.basicConfig(level=_logging.DEBUG, format="%(asctime)s %(threadName)s %(levelname)-7s %(message)s")
        
        self.root = Tkinter.Tk()

        def on_closing():
            # don't let it close (should cancel here)
            pass

        self.root.title("Preview")

        cv = Tkinter.Canvas(width=self.video_config.width, height=self.video_config.height)
        cv.pack(side='top', fill='both')

        self.root.protocol("WM_DELETE_WINDOW", on_closing)

        def update_image(data):
            try:
                photo_f = StringIO()
                photo_f.write('P6\n')
                photo_f.write('{}\n'.format(self.video_config.width))
                photo_f.write('{}\n'.format(self.video_config.height))
                photo_f.write('255\n')

                ppm_data = bytearray(len(data) // 4 * 3)
                
                for i in xrange(len(data) // 4):
                    ppm_data[i * 3 + 0] = data[i * 4 + 2]
                    ppm_data[i * 3 + 1] = data[i * 4 + 1]
                    ppm_data[i * 3 + 2] = data[i * 4 + 0]
                    
                photo_f.write(ppm_data)
                
                self.photo = Tkinter.PhotoImage(data=photo_f.getvalue())
                cv.create_image(0, 0, image=self.photo, anchor='nw')
                cv.pack(side='top', fill='both')
                self.out_queue.put("ready")
            except:
                logger.exception("Exception producing image")
                raise

            
        def tick():
            try:
                item = self.in_queue.get(False)

                if item == _STOP:
                    self.root.destroy()
                    return
                elif isinstance(item, Image):
                    update_image(item.data)
            except:
                pass
            
            self.root.after(100, tick)
        
        self.root.after(100, tick)
        self.root.mainloop()
    
    def __init__(self, video_config):
        self.video_config = video_config
        self.in_queue = Queue()
        self.out_queue = Queue()
        self.ready_for_image = True
        self.frames_since_last_render = 0
    
    def show_preview_ui(self):
        self.thread = Process(target=self._ui_thread)
        self.thread.start()

    def update_image(self, imagedata):
        if not self.ready_for_image:
            try:
                self.out_queue.get(False) # if there's ANYTHING in the queue, treat it as ready
                self.ready_for_image = True
            except Empty:
                # Skip frame because still rendering last frame
                pass
            
        if self.ready_for_image:
            # after ready, wait as many frames as were produced during the preview before we render the next one, to give the rendering process some breathing room
            
            if self.frames_since_last_render != 0:
                self.frames_since_last_render -= 1
            else:
                self.ready_for_image = False
                self.in_queue.put(Image(imagedata))
        else:
            self.frames_since_last_render += 1
        
    def destroy_preview_ui(self):
        self.in_queue.put(_STOP)
        
