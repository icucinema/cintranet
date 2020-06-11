# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SKUTicketType'
        db.create_table(u'icusync_skutickettype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sku', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['icusync.SKU'])),
            ('ticket_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ticketing.TicketType'])),
        ))
        db.send_create_signal(u'icusync', ['SKUTicketType'])


    def backwards(self, orm):
        # Deleting model 'SKUTicketType'
        db.delete_table(u'icusync_skutickettype')


    models = {
        u'icusync.authenticationcredential': {
            'Meta': {'object_name': 'AuthenticationCredential'},
            'auth_data': ('django.db.models.fields.TextField', [], {}),
            'auth_slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'icusync.product': {
            'Meta': {'object_name': 'Product'},
            'currently_available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'eactivities_id': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'org_id': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sold': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'icusync.sku': {
            'Meta': {'object_name': 'SKU'},
            'dirty': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'eactivities_id': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'org_id': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['icusync.Product']"}),
            'sold': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'icusync.skuentitlement': {
            'Meta': {'object_name': 'SKUEntitlement'},
            'entitlement': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ticketing.Entitlement']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sku': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['icusync.SKU']"}),
            'uses_remaining': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'icusync.skutickettype': {
            'Meta': {'object_name': 'SKUTicketType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sku': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['icusync.SKU']"}),
            'ticket_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ticketing.TicketType']"})
        },
        u'ticketing.baseticketinfo': {
            'Meta': {'ordering': "['sale_price']", 'object_name': 'BaseTicketInfo'},
            'box_office_return_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'general_availability': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'online_description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'print_template_extension': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'sale_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'sell_on_the_door': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sell_online': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'ticketing.entitlement': {
            'Meta': {'object_name': 'Entitlement'},
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'entitled_to': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'entitlements'", 'symmetrical': 'False', 'to': u"orm['ticketing.BaseTicketInfo']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'punters': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'entitlements'", 'symmetrical': 'False', 'through': u"orm['ticketing.EntitlementDetail']", 'to': u"orm['ticketing.Punter']"}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'ticketing.entitlementdetail': {
            'Meta': {'unique_together': "(('punter', 'entitlement'),)", 'object_name': 'EntitlementDetail'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'discount': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'entitlement': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entitlement_details'", 'to': u"orm['ticketing.Entitlement']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'punter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entitlement_details'", 'to': u"orm['ticketing.Punter']"}),
            'remaining_uses': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'ticketing.event': {
            'Meta': {'object_name': 'Event'},
            'event_types': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'event_types'", 'null': 'True', 'to': u"orm['ticketing.EventType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'}),
            'showings': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'events'", 'symmetrical': 'False', 'to': u"orm['ticketing.Showing']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'ticketing.eventtype': {
            'Meta': {'object_name': 'EventType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'})
        },
        u'ticketing.film': {
            'Meta': {'ordering': "['sorting_name']", 'object_name': 'Film'},
            'certificate': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '12'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imdb_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            'poster_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'sorting_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'tmdb_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'ticketing.punter': {
            'Meta': {'ordering': "['name']", 'object_name': 'Punter'},
            'cid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'login': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'punter_type': ('model_utils.fields.StatusField', [], {'default': "'full'", 'max_length': '100', u'no_check_for_status': 'True', 'db_index': 'True'}),
            'swipecard': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'})
        },
        u'ticketing.showing': {
            'Meta': {'ordering': "['start_time']", 'object_name': 'Showing'},
            'film': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'showings'", 'to': u"orm['ticketing.Film']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'primary_event': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'primary_showing'", 'unique': 'True', 'null': 'True', 'to': u"orm['ticketing.Event']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'ticketing.tickettemplate': {
            'Meta': {'ordering': "['sale_price']", 'object_name': 'TicketTemplate', '_ormbases': [u'ticketing.BaseTicketInfo']},
            u'baseticketinfo_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ticketing.BaseTicketInfo']", 'unique': 'True', 'primary_key': 'True'}),
            'event_type': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'ticket_templates'", 'symmetrical': 'False', 'to': u"orm['ticketing.EventType']"})
        },
        u'ticketing.tickettype': {
            'Meta': {'ordering': "['sale_price']", 'object_name': 'TicketType', '_ormbases': [u'ticketing.BaseTicketInfo']},
            u'baseticketinfo_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ticketing.BaseTicketInfo']", 'unique': 'True', 'primary_key': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ticketing.Event']"}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ticketing.TicketTemplate']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['icusync']