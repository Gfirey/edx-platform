from capa.correctmap import CorrectMap
from capa.responsetypes import LoncapaResponse

import json
import logging
import requests

log = logging.getLogger(__name__)

class HTMLAcademyResponse(LoncapaResponse):
    
    response_tag = 'htmlacademyresponse'
    allowed_inputfields = ['htmlacademy']
    max_inputfields = 1

    def setup_response(self):
        self.answer_fields = self.inputfields[0]
        # FIXME Why must this be doubled here and in inputfields.py?
        self.course = self.answer_fields.xpath('//course')[0]
        self.task = self.answer_fields.xpath('//task')[0]

    def get_score(self, student_answers):

        def make_cmap(status = 'incorrect', points = 0, msg = ''):
            return CorrectMap(self.answer_id, status, npoints = points, msg = msg)

        log.info('\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        log.info(student_answers)
        log.info(self.answer_id)

        # Get stat for current user
        from crequest.middleware import CrequestMiddleware
        current_request = CrequestMiddleware.get_request()
        user = current_request.user
        ext_responce = self.do_external_request(user.username)

        # If any arror occured -- we are done
        if (isinstance(ext_responce, dict) and ext_responce.error is not None):
            return make_cmap(msg = ext_responce.error)
        
        # Find course we are checking
        for el in ext_responce:
          # FIXME Pretty brave assumption, make it error-prone 
          if (int(self.course.text) == el['course_id']):
            points_earned = float(el['tasks_completed']) / el['tasks_total'] * self.get_max_score()
            # Ew, grosse!
            points_earned = round(points_earned * 100) / float(100)
            return make_cmap(status = 'correct', points = points_earned)
        
        return make_cmap() 

    def get_answers(self):
        return {} 

    @classmethod
    def do_external_request(kls, ssoid, course = 'basic'):

        # FIXME Hardcoded url
        url = 'http://htmlacademy.ru/api/get_progress?course={1}&ifmo_user_id={0}'.format(ssoid, course)

        try:
            req = requests.post(url)
        except Exception as err:
            msg = 'Cannot connect to HTMLAcademy: %s' % err
            log.error(msg)
            return json.loads('{\'error\': \'%s\'}' % msg)

        #if self.system.DEBUG:
            log.info('response = %s', req.text)

        if (not req.text) or (not req.text.strip()):
            msg = 'Empty answer from HTMLAcademy.'
            log.error(msg)
            return json.loads('{\'error\': \'%s\'}' % msg)

        try:
            # response is JSON; parse it
            rjson = json.loads(req.text)
        except Exception as err:
            msg = 'Cannot parse response from HTMLAcademy.'
            msg_detailed = '{0}. Details:\n    error: {1},\n    data: {2}'.format(msg, err, req.text)
            log.error(msg_detailed)
            return json.loads('{\'error\': \'%s\'}' % msg)

        return rjson
