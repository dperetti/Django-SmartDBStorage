import hashlib
import logging
from compressor.utils import get_class
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch
import os
import re
from django.core.files.storage import Storage, DefaultStorage
from django.db import transaction
from django.utils.encoding import force_unicode
from django.utils.text import get_valid_filename
import sys
from .file import DBStorageFile
from .models import DBFile, DBFileChunk, DBPool


class SmartDBStorage(Storage):
    def __init__(self, option=None):
        self._extraction_storage = get_class(settings.SMARTDBSTORAGE_EXTRACTION_STORAGE)()
        self._serve_directly = settings.SMARTDBSTORAGE_SERVE_DIRECTLY

        if option:
            if 'extraction_storage' in option:
                self._extraction_storage = option['extraction_storage']
            if 'serve_directly' in option:
                self._serve_directly = option['serve_directly']

        if self._extraction_storage is None:
            self._extraction_storage = DefaultStorage()
        if self._serve_directly is None:
            self._serve_directly = False

    def _getDBFile(self, name):
        prefix, name = name.split('/', 1)
        dbfile = DBFile.objects.get(pool__name=prefix, name=name)
        return dbfile

    def _open(self, name, mode='rb'):
        """
        Retrieves the specified file from storage.
        """
        prefix, name = name.split('/', 1)
        return DBStorageFile(prefix=prefix, name=name)

    @transaction.commit_on_success
    def _save(self, name, content):
        """
        Saves new content to the file specified by name. The content should be a
        proper File object, ready to be read from the beginning.
        """

        prefix, name = name.split('/', 1)

        original_name = os.path.basename(content.name)
        if original_name is None:
            original_name = os.path.basename(name)

        pool, created = DBPool.objects.get_or_create(name=prefix)
        dbfile = DBFile(
            pool=pool,
            original_name=original_name,
            size=content.size,
            checksum=''
        )
        dbfile.save()
        i = 0
        m = hashlib.md5()
        for chunk in content.chunks():
            file_chunk = DBFileChunk(
                dbfile=dbfile,
                order=i,
                data=chunk
            )
            m.update(chunk)
            file_chunk.save()
            i += 1
        dbfile.checksum = m.hexdigest()

        # Store filenames with forward slashes, even on Windows
        dbfile.name = str(dbfile.pk) + '/' + self.get_valid_name(dbfile.original_name).replace('\\', '/')
        dbfile.save()

        return dbfile.pool.name + '/' + dbfile.name

    # These methods are part of the public API, with default implementations.
    def url(self, name):
        """
        Returns an absolute URL where the file's contents can be accessed
        directly by a Web browser.
        """
        prefix, _name = name.split('/', 1)

        if not self._serve_directly:

            if self._extraction_storage:
                fs = self._extraction_storage
                if not fs.exists(name):
                    fs.save(name, self.open(name))
                return fs.url(name)

        try:
            dummy = DBFile(pool__name=prefix, name=_name)  # don't hit the database
            return dummy.get_absolute_url()
        except NoReverseMatch, e:
            logging.error("SmartDBStorage is set to serve files directly, but urls.py is not configured to do so.")
            logging.error("Add the following to your url patterns :")
            logging.error("(r'^your_url_prefix_to_serve_files/', include('smartdbstorage.urls', namespace='smart_db_storage'))")

            raise ImproperlyConfigured("Pas bon")

    def get_valid_name(self, name):
        """
        Returns a filename, based on the provided filename, that's suitable for
        use in the target storage system.
        """
        return get_valid_filename(name)
        # # Like get_valid_filename(), but also allow slashes ('/').
        # s = name
        # s = force_unicode(s).strip().replace(' ', '_')
        # return re.sub(r'(?u)[^-\w./]', '', s)

    def exists(self, name):
        """
        Returns True if a file referenced by the given name already exists in the
        storage system, or False if the name is available for a new file.
        """
        try:
            self._getDBFile(name)
            return True
        except DBFile.DoesNotExist:
            return False

    def size(self, name):
        """
        Returns the total size, in bytes, of the file specified by name.
        """
        dbfile = self._getDBFile(name)
        return dbfile.size

    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        return name

    # The following methods form the public API for storage systems
    def delete(self, name):
        """
        Deletes the specified file from the storage system.
        """
        dbfile = self._getDBFile(name)
        dbfile.delete()

    def listdir(self, path):
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files.
        """
        raise NotImplementedError()

    def accessed_time(self, name):
        """
        Returns the last accessed time (as datetime object) of the file
        specified by name.
        """
        raise NotImplementedError()

    def created_time(self, name):
        """
        Returns the creation time (as datetime object) of the file
        specified by name.
        """
        dbfile = self._getDBFile(name)
        return dbfile.created_at

    def modified_time(self, name):
        """
        Returns the last modified time (as datetime object) of the file
        specified by name.
        """
        raise NotImplementedError()