# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'FilmQuotation.valid_from'
        db.add_column(u'pointofsale_filmquotation', 'valid_from',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True, blank=True),
                      keep_default=False)

        # Adding field 'FilmQuotation.valid_to'
        db.add_column(u'pointofsale_filmquotation', 'valid_to',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'FilmQuotation.valid_from'
        db.delete_column(u'pointofsale_filmquotation', 'valid_from')

        # Deleting field 'FilmQuotation.valid_to'
        db.delete_column(u'pointofsale_filmquotation', 'valid_to')


    models = {
        u'pointofsale.filmquotation': {
            'Meta': {'object_name': 'FilmQuotation'},
            'added_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'added_by': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'film_title': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quotation': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'valid_from': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'valid_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'pointofsale.printer': {
            'Meta': {'object_name': 'Printer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'default': 'False', 'unique': 'True', 'max_length': '256'})
        }
    }

    complete_apps = ['pointofsale']