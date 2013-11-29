
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
from student import views as student_views

import logging

log = logging.getLogger(__name__)


@require_POST
def change_enrollment(request):
    """
    This change_enrollment overloads default one. When 'enroll' action is
    specified it tries to lookup in configuration whether some url for the 
    enrolling course is set. If it is so, client is redirected to this url, 
    otherwise standard action is executed and nothing changes.
    """
    # Execute original handler
    response = student_views.change_enrollment(request)
    
    action = request.POST.get("enrollment_action")
    course_id = request.POST.get("course_id")
    callback_url = None

    # Try to lookup redirect url for course if we are enrolling
    if action is not None and action == 'enroll':
        if course_id is not None:
            try:
                callback_url = settings.ENROLL_URL_CALLBACK[course_id]
            except:
                log.debug('No url for course {0} is specified in cofiguration.'.format(course_id))
         
    # If url IS specified -- redirect there
    if callback_url is not None:
      return HttpResponse(callback_url)
    
    # Return original response
    return response
