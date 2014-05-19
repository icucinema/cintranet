# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'StatsData'
        db.create_table(u'stats_statsdata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('jsonfield.fields.JSONField')()),
        ))
        db.send_create_signal(u'stats', ['StatsData'])


    def backwards(self, orm):
        # Deleting model 'StatsData'
        db.delete_table(u'stats_statsdata')


    models = {
        u'stats.statsdata': {
            'Meta': {'object_name': 'StatsData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('jsonfield.fields.JSONField', [], {})
        }
    }

    complete_apps = ['stats']