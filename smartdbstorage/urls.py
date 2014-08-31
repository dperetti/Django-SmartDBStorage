import django
if django.VERSION[:2] < (1, 6):
    from django.conf.urls.defaults import patterns, include, url
else:
    from django.conf.urls import patterns, include, url
from smartdbstorage.views import DBFileView

# This url is used when SMARTDBSTORAGE_SERVE_DIRECTLY=True
# Your project needs to inlude smartdbstorage urls like this :
# urlpatterns = patterns('',
#     url(r'^myapp/', include('myapp.urls')),
#
#     url(r'^dbstorage/', include('smartdbstorage.urls', namespace='smart_db_storage')),
#
# )

urlpatterns = patterns('',
    url(r'^file/(?P<prefix>[^/]+)/(?P<name>.*)$', DBFileView.as_view(), name="file")
)
