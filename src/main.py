# -*- coding: utf-8-unix -*-

from __future__ import division

import math

from ittomp4.views.mod_pattern_view import ModPatternView
from ittomp4.views.mod_header_view import ModHeaderView
from ittomp4.views.framer import Framer
from ittomp4.surface_handler import SurfaceHandler
from ittomp4.types import Config, VideoConfig, AudioConfig
from ittomp4.ffmpegwriter import VideoRunner
from ittomp4.decoder import mod
from ittomp4.types import makerect

from preview import Preview

_config = Config(VideoConfig(1920, 1080, 60),
                 AudioConfig(48000))

class Main(object):
    def _audio_frames_to_next_video_frame(self, state):
        audio_frames_per_video_frame = self.config.audio.fps / self.config.video.fps
        
        overshoot = state['audio']['frames_produced'] % audio_frames_per_video_frame
        return int(math.ceil(audio_frames_per_video_frame - overshoot))

    def main(self, filename):
        self.config = _config

        audio_producer = mod.Decoder(self.config.audio, filename)

        header_view = ModHeaderView(audio_producer)
        pattern_view = ModPatternView(audio_producer)
        root_view = Framer()
        root_view.add(header_view, makerect(0,
                                            0,
                                            self.config.video.width,
                                            self.config.video.height / 30))
        
        root_view.add(pattern_view, makerect(0,
                                             self.config.video.height / 30,
                                             self.config.video.width,
                                             self.config.video.height - (self.config.video.height / 30)))
        
        video_producer = SurfaceHandler(self.config.video, root_view)

        state = {'video': {'frames_produced': 0},
                 'audio': {'frames_produced': 0},
                 'frame': 0,
                 'elapsed_sec': 0.0}
        
        preview = Preview(self.config.video)
        
        def get_frames():
            # TODO: Move this function into a sequencer

            video = video_producer.render(state)
            
            preview.update_image(video)
            
            audio_frames_required = self._audio_frames_to_next_video_frame(state)
            audio = audio_producer.render(audio_frames_required)

            state['video']['frames_produced'] += 1
            state['audio']['frames_produced'] += audio_frames_required
            state['frame'] += 1
            state['elapsed_sec'] = state['frame'] / self.config.video.fps
            
            if video is None or audio is None or preview.is_stop_requested():
                return None
            else:
                return video, audio

        preview.show_preview_ui()
        try:
            ffmpegger = VideoRunner(self.config)
            ffmpegger.start(get_frames)
        finally:
            preview.destroy_preview_ui()
            

if __name__ == '__main__':
    import logging
    import argparse
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(threadName)s %(levelname)-7s %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument('filename')

    args = parser.parse_args()

    from datetime import datetime
    dt_start = datetime.utcnow()
    Main().main(args.filename)
    dt_end = datetime.utcnow()

    from dateutil.relativedelta import relativedelta
    attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
    human_readable = lambda delta: ' '.join(['%d %s' % (getattr(delta, attr), getattr(delta, attr) > 1 and attr or attr[:-1]) 
                                             for attr in attrs if getattr(delta, attr)])

    logging.debug("Finished in {}".format(human_readable(relativedelta(dt_end, dt_start))))
    
