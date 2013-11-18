import django
if django.VERSION[:2] < (1, 6):
    from django.conf.urls.defaults import patterns, include, url
else:
    from django.conf.urls import patterns, include, url
from smartdbstorage.views import DBFileView

urlpatterns = patterns('',
    #url(r'^file/(?P<pk>\d+)/$', DBFileView.as_view(), name="dbfile_view")
    url(r'^file/(?P<prefix>[^/]+)/(?P<name>.*)$', DBFileView.as_view(), name="file")
)
