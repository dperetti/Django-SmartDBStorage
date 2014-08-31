# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    """
    Get rid of the old _data base64 text field, which is now replaced with a binary field.
    """
    dependencies = [
        ('smartdbstorage', '0003_auto_20140831_1743'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dbfilechunk',
            name='_data',
        ),
    ]
