# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table(u'imly_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('super_category', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sub_categories', null=True, to=orm['imly.Category'])),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal(u'imly', ['Category'])

        # Adding M2M table for field tags on 'Category'
        db.create_table(u'imly_category_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('category', models.ForeignKey(orm[u'imly.category'], null=False)),
            ('tag', models.ForeignKey(orm[u'imly.tag'], null=False))
        ))
        db.create_unique(u'imly_category_tags', ['category_id', 'tag_id'])

        # Adding model 'Tag'
        db.create_table(u'imly_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'imly', ['Tag'])

        # Adding model 'Location'
        db.create_table(u'imly_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'imly', ['Location'])

        # Adding model 'Store'
        db.create_table(u'imly_store', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('owner', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('store_contact_number', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('description_html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('tagline', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('cover_photo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('pick_up', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pick_up_address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('pick_up_location', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('provide_delivery', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('facebook_link', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('twitter_link', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('is_open', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('store_notice', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('is_approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('delivery_points', self.gf('django.contrib.gis.db.models.fields.MultiPointField')(default='MULTIPOINT(72.8258 18.9647)')),
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

        # Adding M2M table for field tags on 'Store'
        db.create_table(u'imly_store_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('store', models.ForeignKey(orm[u'imly.store'], null=False)),
            ('tag', models.ForeignKey(orm[u'imly.tag'], null=False))
        ))
        db.create_unique(u'imly_store_tags', ['store_id', 'tag_id'])

        # Adding model 'DeliveryLocation'
        db.create_table(u'imly_deliverylocation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('store', self.gf('django.db.models.fields.related.ForeignKey')(related_name='delivery_locations', blank=True, to=orm['imly.Store'])),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')(default='POINT(72.8258 18.9647)', blank=True)),
            ('bounds', self.gf('django.contrib.gis.db.models.fields.PolygonField')(default=u'POLYGON ((19.2695223999999996 72.9800522999999970, 19.2695223999999996 72.7759056000000015, 18.8933086999999986 72.7759056000000015, 18.8933086999999986 72.9800522999999970, 19.2695223999999996 72.9800522999999970))', blank=True)),
            ('data', self.gf('plata.fields.JSONField')(default='{}', blank=True)),
        ))
        db.send_create_signal(u'imly', ['DeliveryLocation'])

        # Adding model 'Product'
        db.create_table(u'imly_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('_unit_price', self.gf('django.db.models.fields.DecimalField')(max_digits=18, decimal_places=0)),
            ('tax_included', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tax_class', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.TaxClass'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('quantity_per_item', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('quantity_by_price', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('capacity_per_day', self.gf('django.db.models.fields.IntegerField')()),
            ('previous_cpd', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('items_in_stock', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description_html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('lead_time', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('lead_time_unit', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['imly.Category'])),
            ('store', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['imly.Store'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('is_featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_bestseller', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('position', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'imly', ['Product'])

        # Adding unique constraint on 'Product', fields ['name', 'store']
        db.create_unique(u'imly_product', ['name', 'store_id'])

        # Adding M2M table for field tags on 'Product'
        db.create_table(u'imly_product_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('product', models.ForeignKey(orm[u'imly.product'], null=False)),
            ('tag', models.ForeignKey(orm[u'imly.tag'], null=False))
        ))
        db.create_unique(u'imly_product_tags', ['product_id', 'tag_id'])

        # Adding model 'UserProfile'
        db.create_table(u'imly_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('about_me', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('about_me_html', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('cover_profile_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('word_one', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('word_two', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('word_three', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('avatar', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'imly', ['UserProfile'])

        # Adding model 'ChefTip'
        db.create_table(u'imly_cheftip', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('tip_contact_number', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('your_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=50)),
            ('create', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'imly', ['ChefTip'])


    def backwards(self, orm):
        # Removing unique constraint on 'Product', fields ['name', 'store']
        db.delete_unique(u'imly_product', ['name', 'store_id'])

        # Deleting model 'Category'
        db.delete_table(u'imly_category')

        # Removing M2M table for field tags on 'Category'
        db.delete_table('imly_category_tags')

        # Deleting model 'Tag'
        db.delete_table(u'imly_tag')

        # Deleting model 'Location'
        db.delete_table(u'imly_location')

        # Deleting model 'Store'
        db.delete_table(u'imly_store')

        # Removing M2M table for field categories on 'Store'
        db.delete_table('imly_store_categories')

        # Removing M2M table for field delivery_areas on 'Store'
        db.delete_table('imly_store_delivery_areas')

        # Removing M2M table for field tags on 'Store'
        db.delete_table('imly_store_tags')

        # Deleting model 'DeliveryLocation'
        db.delete_table(u'imly_deliverylocation')

        # Deleting model 'Product'
        db.delete_table(u'imly_product')

        # Removing M2M table for field tags on 'Product'
        db.delete_table('imly_product_tags')

        # Deleting model 'UserProfile'
        db.delete_table(u'imly_userprofile')

        # Deleting model 'ChefTip'
        db.delete_table(u'imly_cheftip')


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
            'Meta': {'ordering': "['position', 'name']", 'object_name': 'Category'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'super_category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sub_categories'", 'null': 'True', 'to': u"orm['imly.Category']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['imly.Tag']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'imly.cheftip': {
            'Meta': {'object_name': 'ChefTip'},
            'create': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'tip_contact_number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'your_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'imly.deliverylocation': {
            'Meta': {'object_name': 'DeliveryLocation'},
            'bounds': ('django.contrib.gis.db.models.fields.PolygonField', [], {'default': "u'POLYGON ((19.2695223999999996 72.9800522999999970, 19.2695223999999996 72.7759056000000015, 18.8933086999999986 72.7759056000000015, 18.8933086999999986 72.9800522999999970, 19.2695223999999996 72.9800522999999970))'", 'blank': 'True'}),
            'data': ('plata.fields.JSONField', [], {'default': "'{}'", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'default': "'POINT(72.8258 18.9647)'", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'delivery_locations'", 'blank': 'True', 'to': u"orm['imly.Store']"})
        },
        u'imly.location': {
            'Meta': {'ordering': "['name']", 'object_name': 'Location'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'imly.product': {
            'Meta': {'ordering': "['position', 'store']", 'unique_together': "(('name', 'store'),)", 'object_name': 'Product'},
            '_unit_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '0'}),
            'capacity_per_day': ('django.db.models.fields.IntegerField', [], {}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['imly.Category']"}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'is_bestseller': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'items_in_stock': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'lead_time': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'lead_time_unit': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'previous_cpd': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'quantity_by_price': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'quantity_per_item': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['imly.Store']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['imly.Tag']", 'symmetrical': 'False'}),
            'tax_class': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shop.TaxClass']"}),
            'tax_included': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'imly.store': {
            'Meta': {'ordering': "['-date_created']", 'object_name': 'Store'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['imly.Category']", 'symmetrical': 'False', 'blank': 'True'}),
            'cover_photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'delivery_areas': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['imly.Location']", 'symmetrical': 'False', 'blank': 'True'}),
            'delivery_points': ('django.contrib.gis.db.models.fields.MultiPointField', [], {'default': "'MULTIPOINT(72.8258 18.9647)'"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'description_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'facebook_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'pick_up': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pick_up_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pick_up_location': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'provide_delivery': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'store_contact_number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'store_notice': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tagline': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['imly.Tag']", 'symmetrical': 'False', 'blank': 'True'}),
            'twitter_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'imly.tag': {
            'Meta': {'ordering': "['name']", 'object_name': 'Tag'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'imly.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'about_me': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'about_me_html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'cover_profile_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'word_one': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'word_three': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'word_two': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        u'reviews.revieweditem': {
            'Meta': {'ordering': "('date_added',)", 'object_name': 'ReviewedItem'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reviews'", 'to': u"orm['contenttypes.ContentType']"}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_changed': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'score': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reviews'", 'to': u"orm['auth.User']"})
        },
        u'shop.taxclass': {
            'Meta': {'ordering': "['-priority']", 'object_name': 'TaxClass'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'priority': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        }
    }

    complete_apps = ['imly']