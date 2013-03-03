from django.core.files.base import File
from smartdbstorage.models import DBFile


class DBStorageFile(File):
    def __init__(self, prefix, name):
        self._file = DBFile.objects.get(pool__name=prefix, name=name)

    def chunks(self, chunk_size=None):
        """
        Read the file and yield chunks
        """
        for chunk in self._file.dbfilechunk_set.order_by('order'):
            yield chunk.data

    def read(self):
        content = ''
        for chunk in self.chunks():
            content += chunk
        return content

    @property
    def size(self):
        return self._file.size

    @property
    def name(self):
        return self._file.name
