# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FilmQuotation'
        db.create_table(u'pointofsale_filmquotation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('quotation', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('film_title', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('added_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('added_by', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'pointofsale', ['FilmQuotation'])


    def backwards(self, orm):
        # Deleting model 'FilmQuotation'
        db.delete_table(u'pointofsale_filmquotation')


    models = {
        u'pointofsale.filmquotation': {
            'Meta': {'object_name': 'FilmQuotation'},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'added_by': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'film_title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quotation': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        u'pointofsale.printer': {
            'Meta': {'object_name': 'Printer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'default': 'False', 'unique': 'True', 'max_length': '256'})
        }
    }

    complete_apps = ['pointofsale']