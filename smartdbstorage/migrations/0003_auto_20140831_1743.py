# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_chunks(apps, schema_editor):
    """
    Migrate existing file chunks so they now use a more efficient BinaryField (new in Django 1.6)
    """
    import base64

    DBFileChunk = apps.get_model("smartdbstorage", "DBFileChunk")
    for chunk in DBFileChunk.objects.all().using(schema_editor.connection.alias):
        chunk.datachunk = base64.decodestring(chunk._data)
        chunk.save()

class Migration(migrations.Migration):

    dependencies = [
        ('smartdbstorage', '0002_dbfilechunk_datachunk'),
    ]

    operations = [
        migrations.RunPython(update_chunks)
    ]
