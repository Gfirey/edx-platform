from capa.inputtypes import InputTypeBase
from ifmo_mod.utils import get_current_ssoid, get_current_request, get_current_uri
from hashlib import sha1

class HTMLAcademyInput(InputTypeBase):
    template = 'htmlacademyinput.html'
    tags = ['htmlacademy']

    def setup(self):
        # FIXME Error handling if some fields missing
        self.m_title = self.xml.findtext('./title')
        self.m_description = self.xml.findtext('./description')
        self.m_task = self.xml.findtext('./task')
        self.m_course = self.xml.findtext('./course')
    
        self.m_userid = get_current_ssoid()
        self.m_htmlac_url = self.build_htmlacademy_url()


    def build_htmlacademy_url(self, course = 0, task = 1):
        base_url = 'http://htmlacademy.ru/courses/{0}/run/{1}'.format(course, task)
        result_url = base_url


    def _extra_context(self): 
        return {
            'title': self.m_title,
            'description': self.m_description,
            'task': self.m_task,
            'course': self.m_course,
            'userid': self.m_userid,
            'htmlacademy_url': self.m_htmlac_url
        }
