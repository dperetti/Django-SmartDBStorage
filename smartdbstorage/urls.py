from django.conf.urls.defaults import patterns, include, url
from smartdbstorage.views import DBFileView

urlpatterns = patterns('',
    #url(r'^file/(?P<pk>\d+)/$', DBFileView.as_view(), name="dbfile_view")
    url(r'^file/(?P<prefix>[^/]+)/(?P<name>.*)$', DBFileView.as_view(), name="file")

)
