from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    url(r'signin$', 'ifmo_sso.views.sso_login', {
      'template': 'sso_login_studio.html', 
      'redirect_on_success': settings.SSO_REDIRECT_STUDIO
    }),
    url(r'ifmo_sso/authenticate/', 'ifmo_sso.views.sso_authenticate', {'secret': settings.SSO_SECRET_STUDIO}),
    url(r'^', include('ifmo_sso.urls')),
)
