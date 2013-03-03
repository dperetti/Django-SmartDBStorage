import os
import mimetypes
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import View
from smartdbstorage.models import DBFile


class DBFileView(View):

    def get(self, request, *args, **kwargs):

        print kwargs
        dbfile = None
        try:
            dbfile = DBFile.objects.get(
                pool__name=kwargs['prefix'],
                name=kwargs['name']
            )
        except DBFile.DoesNotExist:
            return HttpResponseNotFound()

        content = ''

        for chunk in dbfile.dbfilechunk_set.order_by('order'):
            content += chunk.data

        content_type = None

        try:
            ext = os.path.splitext(dbfile.name)[1].lower()
            mimetypes.init()
            content_type = mimetypes.types_map[ext]
        except Exception, e:
            content_type = 'application/octet-stream'

        return HttpResponse(
            content=content,
            content_type=content_type,
        )
