FFMPEG = 'ffmpeg'

import logging as _logging
logger = _logging.getLogger(__name__)
import subprocess
import threading

from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
from twisted.internet.interfaces import IPushProducer
from zope.interface import implements


class SourceProducer(object):
    implements(IPushProducer)
    
    FRAMES_DONE = object()

    def __init__(self, source, write_frames, name):
        self._name = name
        self._pause = True
        self._stop = False

        self._pauseLock = threading.Condition()
        
        self._thread = threading.Thread(target=self._produce_frames, args=(source, write_frames,), name=self._name)
        self._thread.start()
        
    def resumeProducing(self):
        self._pauseLock.acquire()
        self._pause = False
        self._pauseLock.notify()
        self._pauseLock.release()

    def pauseProducing(self):
        self._pauseLock.acquire()
        self._pause = True
        self._pauseLock.notify()
        self._pauseLock.release()

    def stopProducing(self):
        self._pauseLock.acquire()
        self._pause = True
        self._stop = True
        self._pauseLock.notify()
        self._pauseLock.release()
    
    def _produce_frames(self, source, write_frames):
        logger.info("Start source producer")

        try:
            frame_generator = source.frames()
            for frame_data in frame_generator:                
                self._pauseLock.acquire()
                try:
                    while self._pause:
                        if self._stop:
                            logger.warning("Stop requested before completion")
                            return

                        logger.debug("Pausing until next frame")
                        self._pauseLock.wait()

                finally:
                    self._pauseLock.release()
                    
                reactor.callFromThread(write_frames, frame_data)


            logger.info("Done producing frames")
        except:
            logger.exception("ERROR producing frames")
        finally:
            reactor.callFromThread(write_frames, SourceProducer.FRAMES_DONE)

            
class SourceWriter(Protocol):
    _started = {}

    def __init__(self, manager, source, name):
        self._name = name
        self._manager = manager
        self._source = source
        self._active = False
    
    def connectionMade(self):
        if self._source in SourceWriter._started:
            logger.warning("Connection made after start")
            self.transport.loseConnection()
            return

        logger.info("Connection established to {}".format(self._name))
        
        self._active = True
        SourceWriter._started[self._source] = True
            
        self._producer = SourceProducer(self._source, self._write_frames, self._name)
        self.transport.registerProducer(self._producer, True)
        self._producer.resumeProducing()

    def connectionLost(self, reason):
        if self._active:
            self._manager.notify_done()
        
    def _write_frames(self, frame_data):
        if frame_data is SourceProducer.FRAMES_DONE:
            logger.info("Dropping connection")
            self.transport.unregisterProducer()
            self.transport.loseConnection()
        else:
            self.transport.write(frame_data)
        
        
class SourceWriterFactory(Factory):
    def __init__(self, manager, source, name):
        self._name = name
        self._manager = manager
        self._source = source
        
    def buildProtocol(self, addr):
        return SourceWriter(self._manager, self._source, self._name)


### Main ###

class Encoder(object):
    def __init__(self, audio_source, video_source):
        """Init a video encoding manager using an audio source and
        a video source.

        video_source and audio_source are objects that implement a
        frames() method.

        source.frames() takes no arguments and returns a generator.
        Each object returned by the generator is a string (bytes) of
        data in the appropriate format for video or audio.

        At the moment, "appropriate format" means:

        audio_source: signed 16-bit little-endian stereo samples,
        interleaved, at 48000 Hz.

        A "single frame" of audio data is two consecutive s16le
        samples: one left channel, one right.

        video_source: bgra data at 1920x1080, to be encoded at 60 fps.

        TODO: audio and video sources should advertise their
        framerates and we should use what they advertise

        """
        self.audio_source = audio_source
        self.video_source = video_source
        
    def notify_done(self):
        self._producers -= 1
        if not self._producers:
            reactor.stop()

    def notify_ffmpeg_exit(self):
        if self._producers:
            logger.error("ffmpeg stopped before producers")
            reactor.stop()
            
    def run(self):
        self._producers = 0
        
        vwf = SourceWriterFactory(self, self.video_source, 'video')
        video_port = reactor.listenTCP(0, vwf).getHost().port
        logger.info("Video server listening on port {}".format(video_port))
        self._producers += 1

        awf = SourceWriterFactory(self, self.audio_source, 'audio')
        audio_port = reactor.listenTCP(0, awf).getHost().port
        logger.info("Audio server listening on port {}".format(audio_port))
        self._producers += 1
        
        def start_ffmpeg():
            def ffmpeg_thread():
                try:
                    process = subprocess.Popen([FFMPEG, '-y',
                                                '-f', 'rawvideo', '-pixel_format', 'bgra', '-video_size', '1920x1080', '-framerate', '60', '-i', 'tcp://127.0.0.1:{}'.format(video_port),
                                                '-f', 's16le', '-ar', '48000', '-ac', '2', '-i', 'tcp://127.0.0.1:{}'.format(audio_port),
                                                '-vsync', '2', '-crf', '15', '-vcodec', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'ultrafast', '-threads', '3', '-c:a', 'libvo_aacenc', '-b:a', '256k', '-movflags', 'faststart', 'out.mp4'])

                    process.wait()
                    if process.returncode != 0:
                        logger.warning("ffmpeg exited with non-zero return code {}".format(process.returncode))
                except:
                    logger.exception("Exception running ffmpeg subprocess")
                finally:
                    reactor.callFromThread(lambda: self.notify_ffmpeg_exit())
                
                
                
            ffmpeg_thread = threading.Thread(target=ffmpeg_thread, name="ffmpeg thread")
            ffmpeg_thread.daemon = True
            ffmpeg_thread.start()
            

        reactor.callWhenRunning(start_ffmpeg)
        reactor.run()
