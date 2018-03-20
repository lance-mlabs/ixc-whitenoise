# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UniqueFile'
        db.create_table(u'ixc_whitenoise_uniquefile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255)),
            ('original_name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255)),
        ))
        db.send_create_signal(u'ixc_whitenoise', ['UniqueFile'])


    def backwards(self, orm):
        # Deleting model 'UniqueFile'
        db.delete_table(u'ixc_whitenoise_uniquefile')


    models = {
        u'ixc_whitenoise.uniquefile': {
            'Meta': {'object_name': 'UniqueFile', 'ordering': "('-pk',)"},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255'}),
            'original_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['ixc_whitenoise']