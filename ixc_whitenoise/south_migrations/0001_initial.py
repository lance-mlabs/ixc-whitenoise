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
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255)),
            ('original_name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=255)),
        ))
        db.send_create_signal(u'ixc_whitenoise', ['UniqueFile'])

        # Adding unique constraint on 'UniqueFile', fields ['name', 'original_name']
        db.create_unique(u'ixc_whitenoise_uniquefile', ['name', 'original_name'])


    def backwards(self, orm):
        # Removing unique constraint on 'UniqueFile', fields ['name', 'original_name']
        db.delete_unique(u'ixc_whitenoise_uniquefile', ['name', 'original_name'])

        # Deleting model 'UniqueFile'
        db.delete_table(u'ixc_whitenoise_uniquefile')


    models = {
        u'ixc_whitenoise.uniquefile': {
            'Meta': {'ordering': "('-pk',)", 'object_name': 'UniqueFile', 'unique_together': "(('name', 'original_name'),)"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255'}),
            'original_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['ixc_whitenoise']