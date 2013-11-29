"""
Module contains helpful some methods.
"""

from crequest.middleware import CrequestMiddleware
from django.conf import settings


def do_external_request(url, allow_empty_answer = True):
    """
    Perform external request to 'url'.

    Returns answer from server. 
    If no empty answer is allowed, then None is returned. 
    If any exception occured None is returned.
    """
    try:
        request = requests.post(url)
    except Exception as err:
        log.error('Cannot connect to {0}: {1}'.format(url, err))
        return None
    if (not allow_empty_answer):
        if (not req.text) or (not req.text.strip()):
          log.error('Empty answer from {0}.'.format(url))
          return None
    return request.text


def get_current_ssoid():
    """
    Retains ssoid of curent user from current session.

    Returns string ssoid.
    If exception occured None is returned.
    """
    ssoid = None
    try:
        current_request = CrequestMiddleware.get_request()
        ssoid = current_request.user.username
    except Exception:
        log.error('Cannot lookup current user ssoid.')
    return ssoid

