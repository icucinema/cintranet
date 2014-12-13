# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Printer'
        db.create_table(u'pointofsale_printer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default=False, unique=True, max_length=256)),
            ('last_seen', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'pointofsale', ['Printer'])


    def backwards(self, orm):
        # Deleting model 'Printer'
        db.delete_table(u'pointofsale_printer')


    models = {
        u'pointofsale.printer': {
            'Meta': {'object_name': 'Printer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'default': 'False', 'unique': 'True', 'max_length': '256'})
        }
    }

    complete_apps = ['pointofsale']