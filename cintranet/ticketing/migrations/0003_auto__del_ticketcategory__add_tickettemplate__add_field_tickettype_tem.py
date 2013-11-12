# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'TicketCategory'
        db.delete_table(u'ticketing_ticketcategory')

        # Adding model 'TicketTemplate'
        db.create_table(u'ticketing_tickettemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('online_description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('sell_online', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sell_on_the_door', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('general_availability', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sale_price', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('box_office_return_price', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'ticketing', ['TicketTemplate'])

        # Adding M2M table for field event_type on 'TicketTemplate'
        m2m_table_name = db.shorten_name(u'ticketing_tickettemplate_event_type')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tickettemplate', models.ForeignKey(orm[u'ticketing.tickettemplate'], null=False)),
            ('eventtype', models.ForeignKey(orm[u'ticketing.eventtype'], null=False))
        ))
        db.create_unique(m2m_table_name, ['tickettemplate_id', 'eventtype_id'])

        # Adding field 'TicketType.template'
        db.add_column(u'ticketing_tickettype', 'template',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ticketing.TicketTemplate'], null=True, blank=True),
                      keep_default=False)

        # Removing M2M table for field category on 'TicketType'
        db.delete_table(db.shorten_name(u'ticketing_tickettype_category'))


    def backwards(self, orm):
        # Adding model 'TicketCategory'
        db.create_table(u'ticketing_ticketcategory', (
            ('box_office_return_price', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('event_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ticketing.EventType'])),
            ('general_availability', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sell_online', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('online_description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('sale_price', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('sell_on_the_door', self.gf('django.db.models.fields.BooleanField')(default=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'ticketing', ['TicketCategory'])

        # Deleting model 'TicketTemplate'
        db.delete_table(u'ticketing_tickettemplate')

        # Removing M2M table for field event_type on 'TicketTemplate'
        db.delete_table(db.shorten_name(u'ticketing_tickettemplate_event_type'))

        # Deleting field 'TicketType.template'
        db.delete_column(u'ticketing_tickettype', 'template_id')

        # Adding M2M table for field category on 'TicketType'
        m2m_table_name = db.shorten_name(u'ticketing_tickettype_category')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tickettype', models.ForeignKey(orm[u'ticketing.tickettype'], null=False)),
            ('ticketcategory', models.ForeignKey(orm[u'ticketing.ticketcategory'], null=False))
        ))
        db.create_unique(m2m_table_name, ['tickettype_id', 'ticketcategory_id'])


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'ticketing.entitlement': {
            'Meta': {'object_name': 'Entitlement'},
            'end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'entitled_to_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'entitled_to_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'punter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entitlements'", 'to': u"orm['ticketing.Punter']"}),
            'remaining_uses': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
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
            'Meta': {'object_name': 'Film'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'ticketing.punter': {
            'Meta': {'object_name': 'Punter'},
            'cid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'login': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'punter_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'swipecard': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'})
        },
        u'ticketing.showing': {
            'Meta': {'object_name': 'Showing'},
            'film': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ticketing.Film']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'ticketing.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'entitlement': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entitlements'", 'null': 'True', 'to': u"orm['ticketing.Entitlement']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'punter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tickets'", 'null': 'True', 'to': u"orm['ticketing.Punter']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'ticket_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tickets'", 'to': u"orm['ticketing.TicketType']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'ticketing.tickettemplate': {
            'Meta': {'object_name': 'TicketTemplate'},
            'box_office_return_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'event_type': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'ticket_templates'", 'symmetrical': 'False', 'to': u"orm['ticketing.EventType']"}),
            'general_availability': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'online_description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'sale_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'sell_on_the_door': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sell_online': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'ticketing.tickettype': {
            'Meta': {'object_name': 'TicketType'},
            'box_office_return_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ticketing.Event']"}),
            'general_availability': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'online_description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'sale_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'sell_on_the_door': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sell_online': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ticketing.TicketTemplate']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ticketing']