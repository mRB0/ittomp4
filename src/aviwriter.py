#!/usr/bin/env python
# -*- coding: utf-8-unix -*-

from __future__ import division

import sys
import logging
import subprocess
import threading
import struct

from Queue import Queue, Empty

from ittomp4 import VideoLayout

FFMPEG = 'ffmpeg'

logger = module_logger = logging.getLogger(__name__)

class RIFFChunk(object):
    def __init__(self, fourcc, data):
        assert(isinstance(fourcc, str) and len(fourcc) == 4)
        self.fourcc = fourcc
        self.data = data

    def __len__(self):
        return len(self.data) + 8 # 8 = 32-bit fourcc + 32-bit data length

    def __str__(self):
        return '{}{}{}'.format(self.fourcc,
                               struct.pack('<I', len(self.data)),
                               self.data)
        

class RIFFList(object):
    def __init__(self, list_fourcc, contents=[], list_tag='LIST'):
        assert(isinstance(list_fourcc, str) and len(list_fourcc) == 4)
        assert(isinstance(list_tag, str) and list_tag in ['RIFF', 'LIST'])
        
        self.list_tag = list_tag
        self.list_fourcc = list_fourcc
        self.contents = contents

    def __len__(self):
        return sum(len(c) for c in self.contents) + 12 # 12 = 32-bit fourcc + 32-bit data+4cc length + list tag

    def __str__(self):
        contents_length = sum(len(c) for c in self.contents)

        return '{}{}{}{}'.format(self.list_tag,
                                 struct.pack('<I', contents_length + 4), # add 4 for 32-bit fourcc
                                 self.list_fourcc,
                                 ''.join(str(c) for c in self.contents))


# - 

class FFMpegRunner(object):
    @classmethod
    def new(cls):
        return FFMpegRunner([FFMPEG, '-y',

                             '-f', 'avi',
                             '-i', '-',

                             '-vsync', '2',
                             '-crf', '15',
                             '-vcodec', 'libx264',
                             '-pix_fmt', 'yuv420p',
                             '-preset', 'ultrafast',
                             '-threads', '3',

                             '-an',
                             #'-c:a', 'libvo_aacenc', '-b:a', '256k',

                             'out.mp4'])
    

    def __init__(self, ffmpeg_command):
        self.ffmpeg_command = ffmpeg_command
        self.process = None

        self.queue = Queue(1)

        self.abortLock = threading.Lock()
        self.aborted = False

    def _start_pipe_logger(self, tag, fobj):
        def pipethread(fobj):
            logger = module_logger.getChild('ffmpeg.{}'.format(tag))
            while True:
                line = fobj.readline()
                if not line:
                    logger.debug("eof from pipe")
                    return
                logger.info(line[:-1])

        t = threading.Thread(target=pipethread,
                             args=[fobj],
                             name="ffmpeg.{}".format(tag))
        t.start()
        

    def _start_video_shuttle(self, writefile):
        def shuttlethread(writefile=writefile):
            try:
                logger = module_logger.getChild('videoshuttle')

                logger.debug("Write avi header")


                avih = RIFFChunk('avih', struct.pack('<IIIIIIIIIIIIII',
                                                     16666,
                                                     0,
                                                     1,
                                                     0x00000100, # flags: 0x100 = AVIF_ISINTERLEAVED
                                                     0,
                                                     0,
                                                     1, # num streams
                                                     8294400, # 1920x1080x4
                                                     1920,
                                                     1080,
                                                     0, 0, 0, 0))

                strh_video = RIFFChunk('strh', struct.pack('<4s4sIHHIIIIIIIIHHHH',
                                                           'vids',
                                                           'DIB ',
                                                           0,
                                                           0,
                                                           0,
                                                           0,
                                                           60, # frames
                                                           1, # per second
                                                           0,
                                                           0, # size of stream (hack)
                                                           0,
                                                           0,
                                                           0x0, # dwSampleSize, "number of bytes of one stream atom"
                                                           0, 0, 0, 0))
                strf_video = RIFFChunk('strf', struct.pack('<IiiHH4sIiiII',
                                                           40, # size of this structure
                                                           1920,
                                                           1080,
                                                           1, # planes (ignored)
                                                           32, # bits per pixel
                                                           'RGBA', # format tag
                                                           0,
                                                           0,
                                                           0,
                                                           0,
                                                           0)) # last 5 ignored by ffmpeg
                                                           
                
                strl_video = RIFFList('strl', [strh_video, strf_video])
                
                hdrl = RIFFList('hdrl', [avih, strl_video])
                
                root = RIFFList('AVI ', [hdrl], 'RIFF')

                with open('debug.avi', 'wb') as avif:
                    avif.write(str(root))
                    
                writefile.write(str(root))
                
                while True:
                    logger.debug('get a frame')
                    frame = self.queue.get()
                    logger.debug("write a frame")
                    written = writefile.write(frame)

                    if written <= 0:
                        logger.debug("couldn't write! stop stop stop")
                        return
            finally:
                dq = self.queue
                self.queue = None
                try:
                    while True:
                        dq.get(False)
                except Empty:
                    pass
                

        t = threading.Thread(target=shuttlethread,
                             args=[],
                             name="shuttle")
        t.start()
    
        
    def start(self):
        def ffmpeg_thread():                
            error_exit = False
            try:
                with self.abortLock:
                    if self.aborted:
                        error_exit = None
                        return
                    self.process = subprocess.Popen(self.ffmpeg_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                
                self._start_pipe_logger('stdout', self.process.stdout)
                self._start_pipe_logger('stderr', self.process.stderr)

                self._start_video_shuttle(self.process.stdin)
                
                self.process.wait()
                
                if self.process.returncode != 0:
                    logger.warning("ffmpeg exited with non-zero return code {}".format(self.process.returncode))
                    error_exit = True
            except:
                logger.exception("Exception running ffmpeg subprocess")
                error_exit = True

            finally:
                dq = self.queue
                if dq is not None:
                    self.queue.put('lol')
                if error_exit is not None:
                    logger.debug("Call ffmpeg exit callback (error={})".format(error_exit))


        ffmpeg_thread = threading.Thread(target=ffmpeg_thread, name="ffmpeg thread")
        ffmpeg_thread.daemon = True
        ffmpeg_thread.start()
        

    def abort(self):
        with self.abortLock:
            self.aborted = True
            if self.process is not None:
                self.process.terminate()

class Main(object):
    def main(self):
        video_producer = VideoLayout(60)

        ffmpegger = FFMpegRunner.new()
        ffmpegger.start()

        for i in range(120):
            frame = video_producer.build_frame()

            q = ffmpegger.queue
            if q is None:
                break
            q.put(frame)

        ffmpegger.abort()
        

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(threadName)s %(levelname)-7s %(message)s")
    
    Main().main()
    
