# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Removing unique constraint on 'DBFile', fields ['prefix', 'name']
        db.delete_unique('smartdbstorage_dbfile', ['prefix', 'name'])

        # Adding model 'DBPool'
        db.create_table('smartdbstorage_dbpool', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal('smartdbstorage', ['DBPool'])

        # Adding field 'DBFile.pool'
        db.add_column('smartdbstorage_dbfile', 'pool', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['smartdbstorage.DBPool']), keep_default=False)

        for d in orm.DBFile.objects.all():
            pool, created = orm.DBPool.objects.get_or_create(name=d.prefix)
            d.pool = pool
            d.save()

        # Deleting field 'DBFile.prefix'
        db.delete_column('smartdbstorage_dbfile', 'prefix')

        # Adding unique constraint on 'DBFile', fields ['name', 'pool']
        db.create_unique('smartdbstorage_dbfile', ['name', 'pool_id'])

    def backwards(self, orm):

        # Removing unique constraint on 'DBFile', fields ['name', 'pool']
        db.delete_unique('smartdbstorage_dbfile', ['name', 'pool_id'])

        # Deleting model 'DBPool'
        db.delete_table('smartdbstorage_dbpool')

        # User chose to not deal with backwards NULL issues for 'DBFile.prefix'
        raise RuntimeError("Cannot reverse this migration. 'DBFile.prefix' and its values cannot be restored.")

        # Deleting field 'DBFile.pool'
        db.delete_column('smartdbstorage_dbfile', 'pool_id')

        # Adding unique constraint on 'DBFile', fields ['prefix', 'name']
        db.create_unique('smartdbstorage_dbfile', ['prefix', 'name'])


    models = {
        'smartdbstorage.dbfile': {
            'Meta': {'unique_together': "(('pool', 'name'),)", 'object_name': 'DBFile'},
            'checksum': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'original_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pool': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['smartdbstorage.DBPool']"}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'smartdbstorage.dbfilechunk': {
            'Meta': {'object_name': 'DBFileChunk'},
            '_data': ('django.db.models.fields.TextField', [], {'db_column': "'data'", 'blank': 'True'}),
            'dbfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['smartdbstorage.DBFile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        },
        'smartdbstorage.dbpool': {
            'Meta': {'object_name': 'DBPool'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['smartdbstorage']
