# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Store'
        db.create_table(u'imly_store', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('owner', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('is_approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'imly', ['Store'])

        # Adding M2M table for field categories on 'Store'
        db.create_table(u'imly_store_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('store', models.ForeignKey(orm[u'imly.store'], null=False)),
            ('category', models.ForeignKey(orm[u'imly.category'], null=False))
        ))
        db.create_unique(u'imly_store_categories', ['store_id', 'category_id'])

        # Adding M2M table for field delivery_areas on 'Store'
        db.create_table(u'imly_store_delivery_areas', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('store', models.ForeignKey(orm[u'imly.store'], null=False)),
            ('location', models.ForeignKey(orm[u'imly.location'], null=False))
        ))
        db.create_unique(u'imly_store_delivery_areas', ['store_id', 'location_id'])

        # Adding model 'Product'
        db.create_table(u'imly_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('capacity_per_month', self.gf('django.db.models.fields.IntegerField')()),
            ('price', self.gf('django.db.models.fields.IntegerField')()),
            ('lead_time', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['imly.Category'])),
            ('store', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['imly.Store'])),
            ('product_image', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_bestseller', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'imly', ['Product'])

        # Adding model 'Category'
        db.create_table(u'imly_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'imly', ['Category'])

        # Adding model 'Location'
        db.create_table(u'imly_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'imly', ['Location'])


    def backwards(self, orm):
        # Deleting model 'Store'
        db.delete_table(u'imly_store')

        # Removing M2M table for field categories on 'Store'
        db.delete_table('imly_store_categories')

        # Removing M2M table for field delivery_areas on 'Store'
        db.delete_table('imly_store_delivery_areas')

        # Deleting model 'Product'
        db.delete_table(u'imly_product')

        # Deleting model 'Category'
        db.delete_table(u'imly_category')

        # Deleting model 'Location'
        db.delete_table(u'imly_location')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'imly.category': {
            'Meta': {'object_name': 'Category'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'imly.location': {
            'Meta': {'object_name': 'Location'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'imly.product': {
            'Meta': {'object_name': 'Product'},
            'capacity_per_month': ('django.db.models.fields.IntegerField', [], {}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['imly.Category']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_bestseller': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lead_time': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price': ('django.db.models.fields.IntegerField', [], {}),
            'product_image': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['imly.Store']"})
        },
        u'imly.store': {
            'Meta': {'object_name': 'Store'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['imly.Category']", 'symmetrical': 'False'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'delivery_areas': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['imly.Location']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['imly']