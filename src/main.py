# -*- coding: utf-8-unix -*-

from __future__ import division

import math

from ittomp4.views.mod_pattern_view import ModPatternView
from ittomp4.surface_handler import SurfaceHandler
from ittomp4.config import Config, VideoConfig, AudioConfig
from ittomp4.ffmpegwriter import VideoRunner
from ittomp4.decoder import mod

_config = Config(VideoConfig(1920, 1080, 60),
                 AudioConfig(48000))

class Main(object):
    def _audio_frames_to_next_video_frame(self, state):
        audio_frames_per_video_frame = self.config.audio.fps / self.config.video.fps
        
        overshoot = state['audio']['frames_produced'] % audio_frames_per_video_frame
        return int(math.ceil(audio_frames_per_video_frame - overshoot))

    def main(self):
        self.config = _config
        
        audio_producer = mod.Decoder(self.config.audio, 'desertrocks.it')
        video_producer = SurfaceHandler(self.config.video, ModPatternView())

        state = {'video': {'frames_produced': 0},
                 'audio': {'frames_produced': 0},
                 'frame': 0,
                 'elapsed_sec': 0.0}
        
        def get_frames():
            # TODO: Move this function into a sequencer
            audio_producer.update_state(state)

            video = video_producer.render(state)
            
            audio_frames_required = self._audio_frames_to_next_video_frame(state)
            audio = audio_producer.render(audio_frames_required)

            state['video']['frames_produced'] += 1
            state['audio']['frames_produced'] += audio_frames_required
            state['frame'] += 1
            state['elapsed_sec'] = state['frame'] / self.config.video.fps
            
            if video is None or audio is None:
                return None
            else:
                return video, audio
            
        ffmpegger = VideoRunner(self.config)
        ffmpegger.start(get_frames)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(threadName)s %(levelname)-7s %(message)s")
    
    Main().main()
