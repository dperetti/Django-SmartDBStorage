import base64

from django.db import models


class DBPool(models.Model):
    name = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return self.name


class DBFile(models.Model):
    pool = models.ForeignKey(DBPool)
    name = models.CharField(max_length=255, db_index=True)
    original_name = models.CharField(max_length=255)
    checksum = models.CharField(max_length=32, db_index=True)
    size = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        unique_together = ('pool', 'name')

    @models.permalink
    def get_absolute_url(self):
        return 'smart_db_storage:file', (), dict(prefix=self.pool.name, name=self.name)


class DBFileChunk(models.Model):
    dbfile = models.ForeignKey(DBFile)
    order = models.IntegerField()
    _data = models.TextField(
        db_column='data',
        blank=True)

    def set_data(self, data):
        self._data = base64.encodestring(data)

    def get_data(self):
        return base64.decodestring(self._data)

    data = property(get_data, set_data)
