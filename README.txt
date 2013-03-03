=====================
Django-SmartDBStorage
=====================

SmartDBStorage is a File Storage for Django that stores files in the database using Django Models.

When the attachments or images are as important as the other data, you may want to store them in the database for better integrity and consistency.

For example, this is specially useful to store original pictures which are displayed using `sorl thumbnail <https://github.com/sorl/sorl-thumbnail>`_.

Advantages : everything at the same place, no more broken links, better flexibility.
Disadvantages : performance, overall data usage.

Features
========

* Minimal configuration : just a pluggable Django app.

* Django model based : No database to create and setup manually. Uses `South <http://south.aeracode.org>`_.

* Files are saved in chunks in order to limit memory usage.

* Original file names are preserved : No more logo_1.jpg, logo_2.jpg, logo_3.jpg "behind the scene" renames. Files a renamed to /some_unique_id/original_file_name.ext.

* Files can be extracted to another File Storage when accessed from the web or be served directly from the database. (not recommended, but useful for debugging purposes)

* Basic admin for inspection purposes.

Caveats
-------

* Django doesn't support blobs yet (planned in 1.6) so file chunks are saved in base64, which increases the overall storage requirements.

Install
=======

In your ``settings.py``, add ``'south'`` (if you don't use it already) and ``'smartdbstorage'`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        'south',
        'smartdbstorage'
    )

In ``settings.py```, it's a good idea to set global defaults::
    
    SMARTDBSTORAGE_SERVE_DIRECTLY = False  # when accessed from the web files are either served directly or extracted to another file storage
    SMARTDBSTORAGE_EXTRACTION_STORAGE = DEFAULT_FILE_STORAGE

In your ``urls.py``, add the following::

    (r'^some_prefix/', include('smartdbstorage.urls', namespace='smart_db_storage')),

This allows to serve files directly from the database if needed.

Example usage
-------------

Simply specify a SmartDBStorage instance where you want to use it::

    class Article(models.Model):
        text = models.TextField()
        image = ImageField(upload_to='articles_images', storage=SmartDBStorage())

You can override defaults like this::

    class Article(models.Model):
        text = models.TextField()
        image = ImageField(upload_to='articles_images', storage=SmartDBStorage(option=dict(extraction_storage=FileSystemStorage())))
