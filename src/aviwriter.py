#!/usr/bin/env python
# -*- coding: utf-8-unix -*-

from __future__ import division

import sys
import logging
import subprocess
import threading
import struct

from Queue import Queue, Empty

from ittomp4 import VideoLayout, ModDecoder

FFMPEG = 'ffmpeg'

logger = module_logger = logging.getLogger(__name__)

from cStringIO import StringIO

class RIFFChunk(object):
    def __init__(self, fourcc, data):
        assert(isinstance(fourcc, str) and len(fourcc) == 4)
        self.fourcc = fourcc
        self.data = data

    def __len__(self):
        return len(self.data) + 8 # 8 = 32-bit fourcc + 32-bit data length

    def dump(self, fobj):
        fobj.write(struct.pack('<4s', self.fourcc))
        fobj.write(struct.pack('<I', len(self.data)))
        fobj.write(self.data)
        

class RIFFList(object):
    def __init__(self, list_fourcc, contents=[], list_tag='LIST'):
        assert(isinstance(list_fourcc, str) and len(list_fourcc) == 4)
        assert(isinstance(list_tag, str) and list_tag in ['RIFF', 'LIST'])
        
        self.list_tag = list_tag
        self.list_fourcc = list_fourcc
        self.contents = contents

    def __len__(self):
        return sum(len(c) for c in self.contents) + 12 # 12 = 32-bit fourcc + 32-bit data+4cc length + list tag
        
    def dump(self, fobj):
        contents_length = sum(len(c) for c in self.contents)
        
        fobj.write(struct.pack('<4s', self.list_tag))
        fobj.write(struct.pack('<I', contents_length + 4)) # add 4 for 32-bit fourcc
        fobj.write(struct.pack('<4s', self.list_fourcc))
        for c in self.contents:
            c.dump(fobj)
        

    
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

                             #'-an',
                             '-c:a', 'libvo_aacenc', '-b:a', '256k',

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

                #writefile = open('debug.avi', 'wb')
                
                def write_avi_header(frame, audio):
                    logger.debug("Write avi header")

                    avih = RIFFChunk('avih', struct.pack('<IIIIIIIIIIIIII',
                                                         16666,
                                                         0,
                                                         1,
                                                         0x00000100, # flags: 0x100 = AVIF_ISINTERLEAVED
                                                         0,
                                                         0,
                                                         2, # num streams
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
                                                               1, # scale (seconds)
                                                               60, # rate (frames per scale)
                                                               0,
                                                               0, # size of stream (hack)
                                                               0,
                                                               0,
                                                               0x0, # dwSampleSize, "number of bytes of one stream atom"
                                                               0, 0, 0, 0))
                    strf_video = RIFFChunk('strf', struct.pack('<IiiHH4sIiiII', # BITMAPINFOHEADER
                                                               40, # biSize - size of this structure
                                                               1920, # biWidth
                                                               -1080, # biHeight (negative for top-down pixel rows)
                                                               1, # biPlanes (ignored by ffmpeg)
                                                               32, # biBitCount - bits per pixel
                                                               '', # biCompression - format tag ('\0\0\0\0' = bgra)
                                                               0, # biSizeImage (ignored by ffmpeg)
                                                               0, # biXPelsPerMeter (ignored by ffmpeg)
                                                               0, # biYPelsPerMeter (ignored by ffmpeg)
                                                               0, # byClrUsed (ignored by ffmpeg)
                                                               0)) # byClrImportant (ignored by ffmpeg)

                    audio_fps = 48000
                    
                    strh_audio = RIFFChunk('strh', struct.pack('<4s4sIHHIIIIIIIIHHHH',
                                                               'auds',
                                                               '\0\0\0\0',
                                                               0,
                                                               0,
                                                               0,
                                                               0,
                                                               1, # scale (seconds)
                                                               audio_fps, # rate (frames per scale)
                                                               0,
                                                               0, # size of stream (hack)
                                                               0,
                                                               0,
                                                               0x0, # dwSampleSize, "number of bytes of one stream atom"
                                                               0, 0, 0, 0))
                    strf_audio = RIFFChunk('strf', struct.pack('<HHIIHHH', # WAVEFORMATEX
                                                               0x0001, # wFormatTag (1 = WAVE_FORMAT_PCM)
                                                               2, # nChannels
                                                               audio_fps, # nSamplesPerSec
                                                               audio_fps * 2 * 2, # nAvgBytesPerSec (sample rates * 16-bit * 2 channels)
                                                               2 * 2, # nBlockAlign (16-bit * 2 channels)
                                                               16, # wBitsPerSample (16 bits <2> * 8)
                                                               0)) # cbSize


                    strl_video = RIFFList('strl', [strh_video, strf_video])
                    strl_audio = RIFFList('strl', [strh_audio, strf_audio])

                    dmlh = RIFFChunk('dmlh', struct.pack('<I', 0xffffffff))
                    odml = RIFFList('odml', [dmlh])

                    hdrl = RIFFList('hdrl', [avih, strl_video, strl_audio, odml])

                    # normally we should have movi lists in the 'AVI ' part of the file, but
                    # for simpler code we're putting them all into the 'AVIX' part.
                    # ffmpeg don't care about that.

                    videochunk = RIFFChunk('{:02x}db'.format(0), frame)
                    audiochunk = RIFFChunk('{:02x}wb'.format(1), audio)
                    
                    movi = RIFFList('movi', [videochunk, audiochunk])

                    root = RIFFList('AVI ', [hdrl, movi], 'RIFF')

                    root.dump(writefile)

                first_frame = [True]
                
                def write_frame(frame, audio):
                    if first_frame[0]:
                        write_avi_header(frame, audio)
                        first_frame[0] = False
                    else:
                        videochunk = RIFFChunk('{:02x}db'.format(0), frame)
                        audiochunk = RIFFChunk('{:02x}wb'.format(1), audio)
                        movi = RIFFList('movi', [videochunk, audiochunk])
                        avix = RIFFList('AVIX', [movi], 'RIFF')

                        avix.dump(writefile)

                
                while True:
                    logger.debug('get a frame')
                    frame, audio = self.queue.get()
                    logger.debug("write a frame")
                    written = write_frame(frame, audio)

                    #if written <= 0:
                    #    logger.debug("couldn't write! stop stop stop")
                    #    return
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
                pass
                logger.debug("FORCE KILLING ffmpeg")
                self.process.terminate()

class Main(object):
    def main(self):
        video_producer = VideoLayout(60)
        audio_producer = ModDecoder('desertrocks.it')

        ffmpegger = FFMpegRunner.new()
        ffmpegger.start()

        for i in range(600):
            frame = video_producer.build_frame()
            audio = audio_producer.get_frames(int(round(48000 / 60)))
            
            q = ffmpegger.queue
            if q is None:
                break
            q.put((frame, audio))

        # TODO: wait for ffmpeg to complete
        #ffmpegger.abort()
        

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(threadName)s %(levelname)-7s %(message)s")
    
    Main().main()
    
