from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    # Basic routes
    url(r'^ifmo_sso/login', 'ifmo_sso.views.sso_login', name='login'),
    url(r'^ifmo_sso/logout/$', 'ifmo_sso.views.sso_logout', name='logout'),
    url(r'^ifmo_sso/logout_back/$', 'ifmo_sso.views.sso_logout_back'),
    url(r'^ifmo_sso/authenticate/$', 'ifmo_sso.views.sso_authenticate'),

    # Override default routes
    url(r'^login$', 'ifmo_sso.views.sso_login'),
    url(r'^logout$', 'ifmo_sso.views.sso_logout'),
    url(r'^register$', 'ifmo_sso.views.sso_login'),

    # Legacy login form, FIXME: Fix availability
    url(r'^login/form$', 'student.views.signin_user'),
)
