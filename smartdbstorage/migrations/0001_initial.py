# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'DBFile'
        db.create_table('smartdbstorage_dbfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('prefix', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('original_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('checksum', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('smartdbstorage', ['DBFile'])

        # Adding unique constraint on 'DBFile', fields ['prefix', 'name']
        db.create_unique('smartdbstorage_dbfile', ['prefix', 'name'])

        # Adding model 'DBFileChunk'
        db.create_table('smartdbstorage_dbfilechunk', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dbfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smartdbstorage.DBFile'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('_data', self.gf('django.db.models.fields.TextField')(db_column='data', blank=True)),
        ))
        db.send_create_signal('smartdbstorage', ['DBFileChunk'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'DBFile', fields ['prefix', 'name']
        db.delete_unique('smartdbstorage_dbfile', ['prefix', 'name'])

        # Deleting model 'DBFile'
        db.delete_table('smartdbstorage_dbfile')

        # Deleting model 'DBFileChunk'
        db.delete_table('smartdbstorage_dbfilechunk')


    models = {
        'smartdbstorage.dbfile': {
            'Meta': {'unique_together': "(('prefix', 'name'),)", 'object_name': 'DBFile'},
            'checksum': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'original_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'smartdbstorage.dbfilechunk': {
            'Meta': {'object_name': 'DBFileChunk'},
            '_data': ('django.db.models.fields.TextField', [], {'db_column': "'data'", 'blank': 'True'}),
            'dbfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['smartdbstorage.DBFile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['smartdbstorage']
