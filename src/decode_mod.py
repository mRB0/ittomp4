# -*- coding: utf-8-unix -*-

import logging as _logging
logger = _logging.getLogger(__name__)

import pybass
import ctypes

_bass_initialized = False

class BASSError(Exception):
    def __init__(self, error_code, fn_name):
        error_description = pybass.error_descriptions.get(error_code, u"(Unrecognized error)")
        
        super(BASSError, self).__init__(u'{}: {}'.format(fn_name, error_description))
        self.error_code = error_code
        
        

def _bass_check_call(fn_name, *args):
    rc = getattr(pybass, fn_name)(*args)
    error_code = pybass.BASS_ErrorGetCode()
    if error_code != 0:
        raise BASSError(error_code, fn_name)
    else:
        return rc
    
    
class Module(object):
    def __init__(self, module_filename):
        if not _bass_initialized:
            logger.info("Initialize BASS")
            _bass_check_call('BASS_Init', 0, 48000, 0, 0, 0)

        # TODO: add unicode support -- encode filename as utf-16 on windows, utf-8 elsewhere
        self.h_mod = _bass_check_call('BASS_MusicLoad', False, module_filename, 0, 0, pybass.BASS_MUSIC_DECODE | pybass.BASS_MUSIC_STOPBACK, 48000)
        
    def decode(self, num_samples):
        buf = (ctypes.c_int16 * num_samples)()
        
        try:
            returned = _bass_check_call('BASS_ChannelGetData', self.h_mod, buf, num_samples * 2) # * 2 => n 16-bit samples = n * 2 bytes
        except BASSError as e:
            if e.error_code == pybass.BASS_ERROR_ENDED:
                logger.debug("End of mod")
                return None
            else:
                raise
            
        returned = returned / 2
        
        if returned < num_samples:
            buf = buf[:returned]

        return list(buf)
    
    def close(self):
        if self.h_mod is not None:
            _bass_check_call('BASS_MusicFree', self.h_mod)
            self.h_mod = None
        
        
