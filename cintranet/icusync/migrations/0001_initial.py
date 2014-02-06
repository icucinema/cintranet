# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AuthenticationCredential'
        db.create_table(u'icusync_authenticationcredential', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('auth_slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('auth_data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'icusync', ['AuthenticationCredential'])

        # Adding model 'Product'
        db.create_table(u'icusync_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('org_id', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('eactivities_id', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('sold', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('initial', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('currently_available', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'icusync', ['Product'])

        # Adding model 'SKU'
        db.create_table(u'icusync_sku', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['icusync.Product'])),
            ('eactivities_id', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('sold', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('initial', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('dirty', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'icusync', ['SKU'])

        # Adding model 'SKUEntitlement'
        db.create_table(u'icusync_skuentitlement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sku', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['icusync.SKU'])),
            ('entitlement', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ticketing.Entitlement'])),
            ('uses_remaining', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'icusync', ['SKUEntitlement'])


    def backwards(self, orm):
        # Deleting model 'AuthenticationCredential'
        db.delete_table(u'icusync_authenticationcredential')

        # Deleting model 'Product'
        db.delete_table(u'icusync_product')

        # Deleting model 'SKU'
        db.delete_table(u'icusync_sku')

        # Deleting model 'SKUEntitlement'
        db.delete_table(u'icusync_skuentitlement')


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
        }
    }

    complete_apps = ['icusync']