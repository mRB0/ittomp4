FFMPEG = 'ffmpeg'

import os
import logging as _logging
logger = _logging.getLogger(__name__)
module_logger = logger
import subprocess
import threading
import ittomp4

from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
from twisted.internet.interfaces import IPushProducer
from zope.interface import implements


class SourceProducerExitOK(object): pass
class SourceProducerExitError(object): pass

class SourceProducer(object):
    implements(IPushProducer)
    
    EXIT_OK = SourceProducerExitOK
    EXIT_ERROR = SourceProducerExitError

    def __init__(self, encode_runner):
        self._encode_runner = encode_runner

        self._pause = True
        self._stop = False

        self._pauseLock = threading.Condition()
        
    def start(self, source_writer):
        self._source_writer = source_writer
        
        self._thread = threading.Thread(target=self._produce_frames,
                                        args=(self._source_writer,),
                                        name="source producer: " + self._source_writer.factory.encode_runner.name)
        self._thread.start()
        
    def resumeProducing(self):
        with self._pauseLock:
            self._pause = False
            self._pauseLock.notify()

    def pauseProducing(self):
        with self._pauseLock:
            self._pause = True
            self._pauseLock.notify()

    def stopProducing(self):
        with self._pauseLock:
            self._pause = True
            self._stop = True
            self._pauseLock.notify()

    def abort(self):
        self._encode_runner.source.abort()
            
    def _produce_frames(self, source_writer):
        logger.info("Start source producer")
        source = source_writer.factory.encode_runner.source
        exit_reason = SourceProducer.EXIT_ERROR
        
        try:
            frame_generator = source.frames()
            for frame_data in frame_generator:                
                with self._pauseLock:
                    while self._pause:
                        if self._stop:
                            logger.warning("Stop requested before completion")
                            return

                        logger.debug("Pausing until next frame")
                        self._pauseLock.wait()

                if isinstance(frame_data, ittomp4.SynchronizerAbort):
                    logger.warning("Synchronizer aborted")
                    return
                elif isinstance(frame_data, ittomp4.SynchronizerDone):
                    break

                reactor.callFromThread(source_writer.write_frames, frame_data)


            logger.info("Done producing frames")
            exit_reason = SourceProducer.EXIT_OK
        except:
            logger.exception("ERROR producing frames")
        finally:
            reactor.callFromThread(source_writer.write_frames, exit_reason)
 
            
class SourceWriter(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.active = False
    
    def connectionMade(self):
        if self.factory.started:
            logger.warning("Connection made after start")
            self.transport.loseConnection()
            return

        logger.info("Connection established to {}".format(self.factory.encode_runner.name))

        self.factory.encode_runner.producer_connection_made()
        
        self.active = True
        self.factory.started = True
            
        self.factory.encode_runner.producer.start(self)
        self.transport.registerProducer(self.factory.encode_runner.producer, True)
        self.factory.encode_runner.producer.resumeProducing()

    def connectionLost(self, reason):
        if self.active:
            self.factory.encode_runner.producer_connection_dropped()
        
    def write_frames(self, frame_data):
        if frame_data is SourceProducer.EXIT_OK or frame_data is SourceProducer.EXIT_ERROR:
            logger.info("Dropping connection")
            self.transport.unregisterProducer()
            self.transport.loseConnection()

            self.factory.encode_runner.producer_done(frame_data is not SourceProducer.EXIT_OK)
        else:
            self.transport.write(frame_data)
        
        
class SourceWriterFactory(Factory):
    def __init__(self):
        self.started = False

    def setEncodeRunner(self, encode_runner):
        self.encode_runner = encode_runner
        
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
                             '-c:a', 'libvo_aacenc', '-b:a', '256k', output_path],
                            'audio',
                            [output_path])
    

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
                            'video',
                            [output_path])
    
                            
    def __init__(self, ffmpeg_command, name, output_paths=[]):
        self.ffmpeg_command = ffmpeg_command
        self.output_paths = output_paths
        self.name = name
        self.process = None

        self.abortLock = threading.Lock()
        self.aborted = False

    def _start_pipe_logger(self, tag, fobj):
        def pipethread(fobj):
            logger = module_logger.getChild('{}.ffmpeg.{}'.format(self.name, tag))
            while True:
                line = fobj.readline()
                if not line:
                    logger.debug("eof from pipe")
                    return
                logger.info(line[:-1])

        t = threading.Thread(target=pipethread,
                             args=[fobj],
                             name="ffmpeg-{}-{}".format(self.name, tag))
        t.start()
        
        
    def start(self, encode_runner):
        def ffmpeg_thread():                
            error_exit = False
            try:
                with self.abortLock:
                    if self.aborted:
                        error_exit = None
                        return
                    self.process = subprocess.Popen(self.ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                
                self._start_pipe_logger('stdout', self.process.stdout)
                self._start_pipe_logger('stderr', self.process.stderr)
                
                self.process.wait()
                
                if self.process.returncode != 0:
                    logger.warning("ffmpeg exited with non-zero return code {}".format(self.process.returncode))
                    error_exit = True
            except:
                logger.exception("Exception running ffmpeg subprocess")
                error_exit = True

            finally:
                if error_exit is not None:
                    logger.debug("Call ffmpeg exit callback (error={})".format(error_exit))
                    reactor.callFromThread(lambda: encode_runner.ffmpeg_done(error_exit))


        ffmpeg_thread = threading.Thread(target=ffmpeg_thread, name="ffmpeg thread")
        ffmpeg_thread.daemon = True
        ffmpeg_thread.start()
        

    def abort(self, encode_runner):
        call_callback = False
        with self.abortLock:
            self.aborted = True
            if self.process is None:
                call_callback = True
            else:
                self.process.terminate()
                
        encode_runner.ffmpeg_done(True)
        


class EncodeRunner(object):
    def __init__(self, encoder, source, ffmpeg_runner, name):
        self.name = name
        self.encoder = encoder
        self.source = source
        self.ffmpeg_runner = ffmpeg_runner
        self.producer = SourceProducer(self)
        
        self.ffmpeg_running = False
        self.producer_running = False
        self.producer_connected = False

        self.failed = False
        self.done = False
        

    def start(self):
        self.ffmpeg_runner.start(self)
        self.ffmpeg_running = True
        self.producer_running = True

    def abort_processes(self):
        logger.debug("@@@@@@@@@@@@@@@ ABORT PROCESSES")
        if self.producer_running:
            logger.debug("Abort producer")
            self.producer.abort()
            self.producer_running = False

        if self.ffmpeg_running:
            logger.debug("Abort ffmpeg")
            self.ffmpeg_runner.abort(self)

        self.failed = True
            
        
    def ffmpeg_done(self, error):
        self.ffmpeg_running = False
        if error:
            self.abort_processes()

        self.check_completion()

    def producer_done(self, error):
        self.producer_running = False
        if error:
            self.abort_processes()
            
        self.check_completion()

    def producer_connection_made(self):
        self.producer_connected = True
        
    def producer_connection_dropped(self):
        self.producer_connected = False

        self.check_completion()

    def check_completion(self):
        logger.debug("check_completion: {}, {}, {}, {}".format(self.producer_running, self.ffmpeg_running, self.producer_connected, self.done))
        if not self.producer_running and not self.ffmpeg_running and not self.producer_connected and not self.done:
            self.done = True
            self.encoder.encode_runner_done(self)

    def abort(self):
        self.abort_processes()
        self.check_completion()
        
### Main ###

from collections import namedtuple
EncodeStatus = namedtuple('EncodeStatus', ('source', 'encode_runner', 'encoded', ))

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
            logger.debug("Stopping reactor")
            reactor.stop()
            self.reactor_running = False
        else:
            logger.error("@@@@@@@@@@@@ manager.stop called more than once @@@@@@@@@@@@")

    def encode_runner_done(self, encode_runner):
        done = all(er.done for er in [self.audio_encode_runner, self.video_encode_runner])
        failed = any(er.failed for er in [self.audio_encode_runner, self.video_encode_runner] if er.done)
        
        if done:
            # all tasks done; some may have failed
            self.all_done()
            
        elif failed:
            # at least one has failed, and not all are done; abort remaining
            for er in [self.audio_encode_runner, self.video_encode_runner]:
                if not er.done:
                    er.abort()
                    
        else:
            # nothing has failed, but not everything is done yet; nothing to do but wait for next
            pass
        
        
    def all_done(self):
        failed = any(er.failed for er in [self.audio_encode_runner, self.video_encode_runner])
        if failed:
            logger.error("STEP 1 ENCODING FAILED")
        else:
            logger.info("Step 1 encode completed")

        self.stop()
        
    def run(self):
        vwf = SourceWriterFactory()
        video_port = reactor.listenTCP(0, vwf).getHost().port
        logger.info("Video server listening on port {}".format(video_port))

        awf = SourceWriterFactory()
        audio_port = reactor.listenTCP(0, awf).getHost().port
        logger.info("Audio server listening on port {}".format(audio_port))

        audio_ffmpeg = FFMpegRunner.new_for_audio(audio_port)
        video_ffmpeg = FFMpegRunner.new_for_video(video_port)

        audio_output = audio_ffmpeg.output_paths
        video_output = video_ffmpeg.output_paths

        # TODO reactor.callWhenRunning(encode_runner.start)

        self.audio_encode_runner = EncodeRunner(self, self.audio_source, audio_ffmpeg, 'audio')
        self.video_encode_runner = EncodeRunner(self, self.video_source, video_ffmpeg, 'video')

        awf.setEncodeRunner(self.audio_encode_runner)
        vwf.setEncodeRunner(self.video_encode_runner)
        
        reactor.callWhenRunning(lambda: self.audio_encode_runner.start())
        reactor.callWhenRunning(lambda: self.video_encode_runner.start())

        self.reactor_running = True
        reactor.run()

        for path in audio_output + video_output:
            os.unlink(path)
                
