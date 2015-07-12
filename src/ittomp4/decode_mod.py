# -*- coding: utf-8-unix -*-

from __future__ import division, absolute_import

import logging as _logging
logger = _logging.getLogger(__name__)

import ctypes

from . import libopenmpt

def _openmpt_log(message, user):
    logger.info("(openmpt) {}".format(message.decode('utf-8')))

_openmpt_log_func = libopenmpt.openmpt_log_func(_openmpt_log)

class Module(object):
    def __init__(self, module_filename):
        with open(module_filename, 'rb') as mod_file:
            mod_data = mod_file.read()

        mod_data_buf = ctypes.create_string_buffer(mod_data, len(mod_data))
        
        self.mod_p = libopenmpt.openmpt_module_create_from_memory(mod_data_buf, len(mod_data_buf), _openmpt_log_func, None, None)
        
    def decode(self, num_frames):
        buf = (ctypes.c_int16 * (num_frames * 2))() # * 2 => stereo
        
        returned = libopenmpt.openmpt_module_read_interleaved_stereo(self.mod_p, 48000, num_frames, buf)
        if returned == 0:
            logger.debug("End of mod")
            return None

        buf = buf[:returned * 2]

        logger.debug("Decoded {} frames".format(returned))
        return buf
    
    def close(self):
        if self.mod_p is not None:
            libopenmpt.openmpt_module_destroy(self.mod_p)
            
            self.mod_p = None
        
        
