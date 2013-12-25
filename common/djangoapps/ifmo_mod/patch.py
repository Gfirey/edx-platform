"""
Patch core.
"""

import capa.inputtypes as capa_input_types
import capa.responsetypes as capa_response_types

from xcapa.inputtypes import HTMLAcademyInput
from xcapa.responsetypes import HTMLAcademyResponse 

from ifmo_mod.patches import course_info


import logging

log = logging.getLogger(__name__)


def dummy_wrapper(callback):
    """
    Dummy for future wrappings. Ignore this.
    """
    callback = callback.__func__
    def _w(self, *args, **kwargs):
        # Do something useful
        return callback(self, *args, **kwargs)
    return _w

def patch():
    """
    Patch core with our own stuff.
    """
    capa_input_types.registry.register(HTMLAcademyInput)
    capa_response_types.__all__.append(HTMLAcademyResponse)

    course_info.patch()

    log.info('Everything is now patched with ifmo_mod.')

