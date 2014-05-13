# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Distributor'
        db.create_table(u'ticketing_distributor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('via_troy', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('royalties_percent', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('royalties_minimum', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'ticketing', ['Distributor'])

        # Adding model 'ShowingsWeek'
        db.create_table(u'ticketing_showingsweek', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('film', self.gf('django.db.models.fields.related.ForeignKey')(related_name='showing_weeks', to=orm['ticketing.Film'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('royalties_percent', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('royalties_minimum', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('royalties_troytastic', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'ticketing', ['ShowingsWeek'])

        # Adding field 'Showing.week'
        db.add_column(u'ticketing_showing', 'week',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='showings', null=True, to=orm['ticketing.ShowingsWeek']),
                      keep_default=False)

        # Adding field 'Film.distributor'
        db.add_column(u'ticketing_film', 'distributor',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ticketing.Distributor'], null=True, on_delete=models.SET_NULL, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Distributor'
        db.delete_table(u'ticketing_distributor')

        # Deleting model 'ShowingsWeek'
        db.delete_table(u'ticketing_showingsweek')

        # Deleting field 'Showing.week'
        db.delete_column(u'ticketing_showing', 'week_id')

        # Deleting field 'Film.distributor'
        db.delete_column(u'ticketing_film', 'distributor_id')


    models = {
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
        u'ticketing.boxofficereturn': {
            'Meta': {'object_name': 'BoxOfficeReturn'},
            'film': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'box_office_returns'", 'to': u"orm['ticketing.Film']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pdf_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'raw_data': ('django.db.models.fields.TextField', [], {}),
            'start_time': ('django.db.models.fields.DateField', [], {})
        },
        u'ticketing.distributor': {
            'Meta': {'object_name': 'Distributor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'royalties_minimum': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'royalties_percent': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'via_troy': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
            'distributor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ticketing.Distributor']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imdb_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            'poster_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'royalties_minimum': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'royalties_percent': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'royalties_troytastic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'week': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'showings'", 'null': 'True', 'to': u"orm['ticketing.ShowingsWeek']"})
        },
        u'ticketing.showingsweek': {
            'Meta': {'object_name': 'ShowingsWeek'},
            'film': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'showing_weeks'", 'to': u"orm['ticketing.Film']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'royalties_minimum': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'royalties_percent': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'royalties_troytastic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'ticketing.ticket': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Ticket'},
            'entitlement': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tickets'", 'null': 'True', 'to': u"orm['ticketing.Entitlement']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'punter': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tickets'", 'null': 'True', 'to': u"orm['ticketing.Punter']"}),
            'status': ('model_utils.fields.StatusField', [], {'default': "'pending_collection'", 'max_length': '100', u'no_check_for_status': 'True', 'db_index': 'True'}),
            'ticket_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tickets'", 'to': u"orm['ticketing.TicketType']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'blank': 'True'})
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

    complete_apps = ['ticketing']