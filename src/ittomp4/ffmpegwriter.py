# -*- coding: utf-8-unix -*-

from __future__ import division, absolute_import

import sys
import logging
import subprocess
import threading
import struct

from Queue import Queue, Empty

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

    def __str__(self):
        sio = StringIO()
        self.dump(sio)
        return sio.getvalue()

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

    def __str__(self):
        sio = StringIO()
        self.dump(sio)
        return sio.getvalue()
        
    def dump(self, fobj):
        contents_length = sum(len(c) for c in self.contents)
        
        fobj.write(struct.pack('<4s', self.list_tag))
        fobj.write(struct.pack('<I', contents_length + 4)) # add 4 for 32-bit fourcc
        fobj.write(struct.pack('<4s', self.list_fourcc))
        for c in self.contents:
            c.dump(fobj)
        

        
# - 

class VideoRunner(object):
    FFMPEG_COMMAND = [FFMPEG, '-y',
                             
                      '-f', 'avi',
                      '-i', '-',
                      
                      '-vsync', '2',
                      '-crf', '13',
                      '-vcodec', 'libx264',
                      '-pix_fmt', 'yuv420p',
                      '-preset', 'veryslow',
                      '-threads', '3',
                      
                      '-c:a', 'libvo_aacenc', '-b:a', '320k',
                      
                      'out.mp4']
    

    def __init__(self, config):
        self.config = config
        self.process = None
        self.first_frame_written = False

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
        

    def _write_avi_header(self, fobj, video_frame, audio_frames):
        logger.debug("Write avi header")

        avih = RIFFChunk('avih', struct.pack('<IIIIIIIIIIIIII',
                                             int(round(1 / self.config.video.fps * 1000000)), # dwMicroSecPerFrame - frame display rate in microseconds (unreliable)
                                             0, # dwMaxBytesPerSec (unreliable)
                                             1, # dwPaddingGranularity
                                             0x00000100, # dwFlags: 0x100 = AVIF_ISINTERLEAVED
                                             0, # dwTotalFrames (unreliable)
                                             0, # dwInitialFrames (ignored)
                                             2, # dwStreams - number of streams
                                             self.config.video.width * self.config.video.height * 4, # bytes per video frame
                                             self.config.video.width,
                                             self.config.video.height,
                                             0, 0, 0, 0)) # (reserved)

        strh_video = RIFFChunk('strh', struct.pack('<4s4sIHHIIIIIIIIHHHH',
                                                   'vids',
                                                   'DIB ',
                                                   0,
                                                   0,
                                                   0,
                                                   0,
                                                   1, # scale (seconds)
                                                   self.config.video.fps, # rate (frames per scale)
                                                   0,
                                                   0, # size of stream (hack)
                                                   0,
                                                   0,
                                                   0x0, # dwSampleSize, "number of bytes of one stream atom"
                                                   0, 0, 0, 0))
        strf_video = RIFFChunk('strf', struct.pack('<IiiHH4sIiiII', # BITMAPINFOHEADER
                                                   40, # biSize - size of this structure
                                                   self.config.video.width, # biWidth
                                                   -self.config.video.height, # biHeight (negative for top-down pixel rows)
                                                   1, # biPlanes (ignored by ffmpeg)
                                                   32, # biBitCount - bits per pixel
                                                   '', # biCompression - format tag ('\0\0\0\0' = bgra)
                                                   0, # biSizeImage (ignored by ffmpeg)
                                                   0, # biXPelsPerMeter (ignored by ffmpeg)
                                                   0, # biYPelsPerMeter (ignored by ffmpeg)
                                                   0, # byClrUsed (ignored by ffmpeg)
                                                   0)) # byClrImportant (ignored by ffmpeg)

        strh_audio = RIFFChunk('strh', struct.pack('<4s4sIHHIIIIIIIIHHHH',
                                                   'auds',
                                                   '\0\0\0\0',
                                                   0,
                                                   0,
                                                   0,
                                                   0,
                                                   1, # scale (seconds)
                                                   self.config.audio.fps, # rate (frames per scale)
                                                   0,
                                                   0, # size of stream (hack)
                                                   0,
                                                   0,
                                                   0x0, # dwSampleSize, "number of bytes of one stream atom"
                                                   0, 0, 0, 0))
        strf_audio = RIFFChunk('strf', struct.pack('<HHIIHHH', # WAVEFORMATEX
                                                   0x0001, # wFormatTag (1 = WAVE_FORMAT_PCM)
                                                   2, # nChannels
                                                   self.config.audio.fps, # nSamplesPerSec
                                                   self.config.audio.fps * 2 * 2, # nAvgBytesPerSec (sample rates * 16-bit * 2 channels)
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

        videochunk = RIFFChunk('{:02x}db'.format(0), video_frame)
        audiochunk = RIFFChunk('{:02x}wb'.format(1), audio_frames)

        movi = RIFFList('movi', [videochunk, audiochunk])

        root = RIFFList('AVI ', [hdrl, movi], 'RIFF')

        fobj.write(str(root))

    def _write_avix_chunk(self, fobj, video_frame, audio_frames):
        videochunk = RIFFChunk('{:02x}db'.format(0), video_frame)
        audiochunk = RIFFChunk('{:02x}wb'.format(1), audio_frames)
        movi = RIFFList('movi', [videochunk, audiochunk])
        avix = RIFFList('AVIX', [movi], 'RIFF')
        
        fobj.write(str(avix))
        
        
    def _write_frame(self, fobj, video_frame, audio_frames):
        if self.first_frame_written:
            self._write_avix_chunk(fobj, video_frame, audio_frames)
        else:
            self._write_avi_header(fobj, video_frame, audio_frames)
            self.first_frame_written = True
        
    def start(self, get_frames_fn):
        error_exit = False

        try:
            self.process = subprocess.Popen(VideoRunner.FFMPEG_COMMAND, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            si = self.process.stdin
        
            self._start_pipe_logger('stdout', self.process.stdout)
            self._start_pipe_logger('stderr', self.process.stderr)

            while True:
                frames = get_frames_fn()
                if frames is None:
                    break
                video_frame, audio_frames = frames

                self._write_frame(si, video_frame, audio_frames)

            logger.debug("Done writing frames!")
        except:
            logger.exception("ERROR writing frames!")
            error_exit = True
        finally:
            logger.debug("Wait for ffmpeg process to stop")
            self.process.stdin.close()
            self.process.wait()

            if self.process.returncode != 0:
                logger.warning("ffmpeg exited with non-zero status {}".format(self.process.returncode))
                error_exit = True

            self.process = None
            
            # todo: check return code

    def abort(self):
        pcs = self.process
        if pcs is not None:
            pcs.terminate()
                
    
