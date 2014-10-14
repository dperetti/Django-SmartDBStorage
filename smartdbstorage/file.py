from django.core.files.base import File
from smartdbstorage.models import DBFile


class DBStorageFile(File):
    def __init__(self, prefix, name, storage, full_name, database=None):
        self.storage = storage
        self.full_name = full_name
        self.database = database
        self._file = DBFile.objects.using(database).get(pool__name=prefix, name=name)

    def extracted_file(self):
        """
        Convenience method to extract and return the file from the extraction storage.
        Can be used from the model like this:
        mymodel.image.file.extracted_file()
        """
        fs = self.storage._extract(self.full_name)
        return fs.open(self.full_name)

    def chunks(self, chunk_size=None):
        """
        Read the file and yield chunks
        """
        for chunk in self._file.dbfilechunk_set.using(self.database).order_by('order'):
            yield bytes(chunk.datachunk)

    def read(self):
        content = bytes()
        for chunk in self.chunks():
            content += chunk

        return content

    @property
    def size(self):
        return self._file.size

    @property
    def name(self):
        return self._file.name
