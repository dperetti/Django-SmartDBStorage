import hashlib
import logging
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch
import os
import re
from django.core.files.storage import Storage, DefaultStorage, FileSystemStorage
from django.db import transaction
from django.db import DEFAULT_DB_ALIAS
from django.utils.encoding import force_unicode
from django.utils.text import get_valid_filename
import sys
from .file import DBStorageFile
from .models import DBFile, DBFileChunk, DBPool
from django.utils.deconstruct import deconstructible
from .utils import get_class

@deconstructible
class SmartDBStorage(Storage):
    def __eq__(self, other):  # https://docs.djangoproject.com/en/1.7/topics/migrations/#custom-deconstruct-method
        return True           # (doesn't seem to be called, though)

    def __init__(self, extraction_storage=None, serve_directly=False, database=None, option=None):
        # option = dummy property for support of legacy migrations
        if extraction_storage:
            self._extraction_storage = extraction_storage
        elif hasattr(settings, 'SMARTDBSTORAGE_EXTRACTION_STORAGE'):
                self._extraction_storage = get_class(settings.SMARTDBSTORAGE_EXTRACTION_STORAGE)()
        else:
            self._extraction_storage = FileSystemStorage()

        if serve_directly is not None:
            self._serve_directly = serve_directly
        else:
            self._serve_directly = getattr(settings, 'SMARTDBSTORAGE_SERVE_DIRECTLY', False)

        if database is not None:
            self._database = database
        else:
            self._database = DEFAULT_DB_ALIAS

    def _getDBFile(self, name):
        prefix, name = self._get_prefix_and_basename_for_read(name)
        dbfile = DBFile.objects.using(self._database).get(pool__name=prefix, name=name)
        return dbfile

    def _open(self, name, mode='rb'):
        """
        Retrieves the specified file from storage.
        """
        prefix, _name = self._get_prefix_and_basename_for_read(name)
        return DBStorageFile(prefix=prefix, name=_name, storage=self, full_name=name, database=self._database)

    @transaction.atomic
    def _save(self, name, content):
        """
        Saves new content to the file specified by name. The content should be a
        proper File object, ready to be read from the beginning.
        """

        prefix, name = self._get_prefix_and_basename_for_save(name)

        if content.name is None:
            original_name = os.path.basename(name)
        else:
            original_name = os.path.basename(content.name)

        pool, created = DBPool.objects.using(self._database).get_or_create(name=prefix)
        dbfile = DBFile(
            pool=pool,
            original_name=original_name,
            size=content.size,
            checksum=''
        )
        dbfile.save(using=self._database)
        i = 0
        m = hashlib.md5()
        for chunk in content.chunks():
            file_chunk = DBFileChunk(
                dbfile=dbfile,
                order=i,
                datachunk=chunk
            )
            m.update(chunk)
            file_chunk.save(using=self._database)
            i += 1
        dbfile.checksum = m.hexdigest()

        # Store filenames with forward slashes, even on Window.
        # Insert the id of the dbfile in the path.
        dbfile.name = str(dbfile.pk) + '/' + self.get_valid_name(dbfile.original_name).replace('\\', '/')
        dbfile.save(using=self._database)

        return dbfile.pool.name + '/' + dbfile.name

    def url(self, name):
        """
        Returns an absolute URL where the file's contents can be accessed
        directly by a Web browser.
        """
        prefix, _name = self._get_prefix_and_basename_for_read(name)

        if not self._serve_directly:

            fs = self._extract(name)
            if fs:
                return fs.url(name)

        try:
            dummy = DBFile(pool__name=prefix, name=_name)  # don't hit the database
            return dummy.get_absolute_url()
        except NoReverseMatch, e:
            logging.error("SmartDBStorage is set to serve files directly, but urls.py is not configured to do so.")
            logging.error("Add the following to your url patterns :")
            logging.error("(r'^your_url_prefix_to_serve_files/', include('smartdbstorage.urls', namespace='smart_db_storage'))")

            raise ImproperlyConfigured("SmartDBStorage is set to serve files directly, but urls.py is not configured to do so.")

    def _extract(self, name):
        """
        Extracts the file from the db to the extraction storage (if it exists) and returns the extraction storage (just
        for convenience).
        If you need to extract manually a file, don't use this.
        See DBStorageFile's extracted_file() method.
        """
        if self._extraction_storage:
            fs = self._extraction_storage
            if not fs.exists(name):
                fs.save(name, self.open(name))
            return fs
        return False

    def _get_prefix_and_basename_for_save(self, name):
        """
        "protected/samples/image.jpg" -> "protected/samples", "image.jpg"
        """
        return name.rsplit('/', 1)

    def _get_prefix_and_basename_for_read(self, name):
        """
        "protected/samples/256/image.jpg" -> "protected/samples", "256/image.jpg"
        """
        ar = name.rsplit('/', 2)
        return ar[0], '/'.join([ar[1], ar[2]])

    #
    # These methods are part of the public API, with default implementations.
    #
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

