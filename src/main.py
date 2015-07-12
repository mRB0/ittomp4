from ittomp4.ittomp4 import ModDecoder, VideoLayout
from ittomp4.ffmpegwriter import VideoRunner


class Main(object):
    def main(self):
        video_producer = VideoLayout(60)
        audio_producer = ModDecoder('desertrocks.it')

        def get_frames():            
            video = video_producer.build_frame()
            audio = audio_producer.get_frames(800)

            if video is None or audio is None:
                return None
            else:
                return video, audio
            
        ffmpegger = VideoRunner()
        ffmpegger.start(get_frames)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(threadName)s %(levelname)-7s %(message)s")
    
    Main().main()
