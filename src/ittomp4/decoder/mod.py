# -*- coding: utf-8-unix -*-

from __future__ import division, absolute_import

import logging as _logging
import struct
import ctypes

from . import libopenmpt


logger = _logging.getLogger(__name__)


def _openmpt_log(message, user):
    logger.info("(openmpt) {}".format(message.decode('utf-8')))

_openmpt_log_func = libopenmpt.openmpt_log_func(_openmpt_log)


class Decoder(object):
    def __init__(self, audio_config, mod_filename):
        self.audio_config = audio_config
        self.filename = mod_filename
        
        with open(self.filename, 'rb') as mod_file:
            mod_data = mod_file.read()

        mod_data_buf = ctypes.create_string_buffer(mod_data, len(mod_data))
        
        self.mod_p = libopenmpt.openmpt_module_create_from_memory(mod_data_buf, len(mod_data_buf), _openmpt_log_func, None, None)

    def get_current_pattern(self):
        return libopenmpt.openmpt_module_get_current_pattern(self.mod_p)

    def get_current_order(self):
        return libopenmpt.openmpt_module_get_current_order(self.mod_p)

    def get_order_count(self):
        return libopenmpt.openmpt_module_get_num_orders(self.mod_p)

    def get_pattern_for_order(self, order_index):
        return libopenmpt.openmpt_module_get_order_pattern(self.mod_p, order_index)

    def get_current_row(self):
        return libopenmpt.openmpt_module_get_current_row(self.mod_p)

    def get_formatted_pattern_data(self, pattern_index):
        row_count = libopenmpt.openmpt_module_get_pattern_num_rows(self.mod_p, pattern_index)
        rows = []

        for row_index in xrange(row_count):
            channels = []
            
            for channel_index in xrange(libopenmpt.openmpt_module_get_num_channels(self.mod_p)):
                channel_formatted_openmptstr = libopenmpt.openmpt_module_format_pattern_row_channel(self.mod_p, pattern_index, row_index, channel_index, 0x7fffffff, 0)
                try:
                    channel_formatted = str(channel_formatted_openmptstr)
                finally:
                    libopenmpt.openmpt_free_string(channel_formatted_openmptstr)

                channel_highlight_openmptstr = libopenmpt.openmpt_module_highlight_pattern_row_channel(self.mod_p, pattern_index, row_index, channel_index, 0x7fffffff, 0)
                try:
                    channel_highlight = str(channel_highlight_openmptstr)
                finally:
                    libopenmpt.openmpt_free_string(channel_highlight_openmptstr)

                channels.append((channel_formatted, channel_highlight))

            rows.append(channels)

        return rows
                
                    

        
    def close(self):
        if self.mod_p is not None:
            libopenmpt.openmpt_module_destroy(self.mod_p)
            self.mod_p = None
        else:
            logger.warning("Attempt to close Decoder twice")
        
    def render(self, count):
        buf = (ctypes.c_int16 * (count * 2))() # * 2 => stereo
        
        returned = libopenmpt.openmpt_module_read_interleaved_stereo(self.mod_p, self.audio_config.fps, count, buf)
        if returned == 0:
            logger.debug("End of mod")
            return None

        buf = buf[:returned * 2]
        
        samples_buffer = ''.join([struct.pack('<h', samp) for samp in buf])

        return samples_buffer

    
