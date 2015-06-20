FFMPEG = 'ffmpeg'

import os
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

    def __init__(self, sourcewriter, write_frames):
        self._sourcewriter = sourcewriter
        self._pause = True
        self._stop = False

        self._pauseLock = threading.Condition()
        
        self._thread = threading.Thread(target=self._produce_frames, args=(sourcewriter.factory.source, write_frames,), name=self._sourcewriter.factory.name)
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
    def __init__(self, factory):
        self.factory = factory
        self.active = False
    
    def connectionMade(self):
        if self.factory.started:
            logger.warning("Connection made after start")
            self.transport.loseConnection()
            return

        logger.info("Connection established to {}".format(self.factory.name))
        
        self.active = True
        self.factory.started = True
            
        self.producer = SourceProducer(self, self._write_frames)
        self.transport.registerProducer(self.producer, True)
        self.producer.resumeProducing()

    def connectionLost(self, reason):
        if self.active:
            self.factory.manager.notify_done()
        
    def _write_frames(self, frame_data):
        if frame_data is SourceProducer.FRAMES_DONE:
            logger.info("Dropping connection")
            self.transport.unregisterProducer()
            self.transport.loseConnection()
        else:
            self.transport.write(frame_data)
        
        
class SourceWriterFactory(Factory):
    def __init__(self, manager, source, name):
        self.started = False
        self.name = name
        self.manager = manager
        self.source = source

    def buildProtocol(self, addr):
        return SourceWriter(self)


class FFMpegRunner(object):
    @classmethod
    def new_for_audio(cls, audio_port):
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mkv') as of:
            output_path = of.name
            
        return FFMpegRunner([FFMPEG, '-y',
                             '-f', 's16le', '-ar', '48000', '-ac', '2', '-i', 'tcp://127.0.0.1:{}'.format(audio_port),
                             '-c:v', 'none',
                             '-c:a', 'libvo_aacenc', '-b:a', '256k', output_path], [output_path])
    

    @classmethod
    def new_for_video(cls, video_port):
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mkv') as of:
            output_path = of.name

        return FFMpegRunner([FFMPEG, '-y',
                             '-f', 'rawvideo',
                             '-pixel_format', 'bgra',
                             '-video_size', '1920x1080',
                             '-framerate', '60',
                             '-i', 'tcp://127.0.0.1:{}'.format(video_port),

                             '-vsync', '2',
                             '-crf', '15',
                             '-vcodec', 'libx264',
                             '-pix_fmt', 'yuv420p',
                             '-preset', 'ultrafast',
                             '-threads', '3',
                             '-c:a', 'none',
                             '-movflags', 'faststart',
                             output_path],
                            [output_path])
    
                            
    def __init__(self, ffmpeg_command, output_paths=[]):
        self.ffmpeg_command = ffmpeg_command
        self.output_paths = output_paths

    def start(self, ffmpeg_exit_callback):
        def ffmpeg_thread():
            error_exit = False
            try:
                process = subprocess.Popen(self.ffmpeg_command)

                process.wait()
                if process.returncode != 0:
                    logger.warning("ffmpeg exited with non-zero return code {}".format(process.returncode))
                    error_exit = True
            except:
                logger.exception("Exception running ffmpeg subprocess")
                error_exit = True

                
            ffmpeg_exit_callback(error_exit)



        ffmpeg_thread = threading.Thread(target=ffmpeg_thread, name="ffmpeg thread")
        ffmpeg_thread.daemon = True
        ffmpeg_thread.start()
        

    

    
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
        self.audio_encoded = False
        self.video_encoded = False
        self.reactor_running = False

    def stop(self):
        if self.reactor_running:
            reactor.stop()
            self.reactor_running = True
        
    def notify_done(self):
        self._producers -= 1
        if not self._producers:
            pass
            #self.stop()

    def try_encode_step1_done(self):
        if self.audio_encoded and self.video_encoded:
            logger.info("Audio and video encoding completed! hoorak")
            self.stop()
        
    def encode_done(self, failed, done_fn):
        def fn():
            if failed:
                logger.error("ffmpeg failed; aborting process")
                self.stop()
                return

            done_fn()
            
            self.try_encode_step1_done()
            
        
        reactor.callFromThread(fn)
    
    def audio_encode_done(self, failed):
        def done_fn():
            self.audio_encoded = True
        self.encode_done(failed, done_fn)
    
    def video_encode_done(self, failed):
        def done_fn():
            self.video_encoded = True
        self.encode_done(failed, done_fn)
        

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

        audio_ffmpeg = FFMpegRunner.new_for_audio(audio_port)
        video_ffmpeg = FFMpegRunner.new_for_video(video_port)

        audio_output = audio_ffmpeg.output_paths
        video_output = video_ffmpeg.output_paths
        
        reactor.callWhenRunning(lambda: audio_ffmpeg.start(self.audio_encode_done))
        reactor.callWhenRunning(lambda: video_ffmpeg.start(self.video_encode_done))

        self.reactor_running = True
        reactor.run()

        for path in audio_output + video_output:
            os.unlink(path)
            
