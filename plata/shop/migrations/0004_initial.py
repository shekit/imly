# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TaxClass'
        db.create_table(u'shop_taxclass', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('rate', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('priority', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'shop', ['TaxClass'])

        # Adding model 'Order'
        db.create_table(u'shop_order', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('billing_company', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('billing_first_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('billing_last_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('billing_address', self.gf('django.db.models.fields.TextField')()),
            ('billing_zip_code', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('billing_city', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('billing_country', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('shipping_same_as_billing', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('shipping_company', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('shipping_first_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('shipping_last_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('shipping_address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('shipping_zip_code', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('shipping_city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('shipping_country', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('confirmed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='orders', null=True, to=orm['auth.User'])),
            ('language_code', self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True)),
            ('status', self.gf('django.db.models.fields.PositiveIntegerField')(default=10)),
            ('_order_id', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('items_subtotal', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=18, decimal_places=10)),
            ('items_discount', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=18, decimal_places=10)),
            ('items_tax', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=18, decimal_places=10)),
            ('shipping_method', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('shipping_cost', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=18, decimal_places=10, blank=True)),
            ('shipping_discount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=18, decimal_places=10, blank=True)),
            ('shipping_tax', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=18, decimal_places=10)),
            ('total', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=18, decimal_places=10)),
            ('paid', self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=18, decimal_places=10)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('data', self.gf('plata.fields.JSONField')(blank=True)),
        ))
        db.send_create_signal(u'shop', ['Order'])

        # Adding model 'OrderItem'
        db.create_table(u'shop_orderitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['shop.Order'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['imly.Product'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('sku', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')()),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('_unit_price', self.gf('django.db.models.fields.DecimalField')(max_digits=18, decimal_places=10)),
            ('_unit_tax', self.gf('django.db.models.fields.DecimalField')(max_digits=18, decimal_places=10)),
            ('tax_rate', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('tax_class', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.TaxClass'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('is_sale', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('_line_item_price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=18, decimal_places=10)),
            ('_line_item_discount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=18, decimal_places=10, blank=True)),
            ('_line_item_tax', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=18, decimal_places=10)),
            ('data', self.gf('plata.fields.JSONField')(blank=True)),
        ))
        db.send_create_signal(u'shop', ['OrderItem'])

        # Adding unique constraint on 'OrderItem', fields ['order', 'product']
        db.create_unique(u'shop_orderitem', ['order_id', 'product_id'])

        # Adding model 'OrderStatus'
        db.create_table(u'shop_orderstatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='statuses', to=orm['shop.Order'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('status', self.gf('django.db.models.fields.PositiveIntegerField')(max_length=20)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'shop', ['OrderStatus'])

        # Adding model 'OrderPayment'
        db.create_table(u'shop_orderpayment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['shop.Order'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('status', self.gf('django.db.models.fields.PositiveIntegerField')(default=10)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('payment_module_key', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('payment_module', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('payment_method', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('transaction_id', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('authorized', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('data', self.gf('plata.fields.JSONField')(blank=True)),
        ))
        db.send_create_signal(u'shop', ['OrderPayment'])


    def backwards(self, orm):
        # Removing unique constraint on 'OrderItem', fields ['order', 'product']
        db.delete_unique(u'shop_orderitem', ['order_id', 'product_id'])

        # Deleting model 'TaxClass'
        db.delete_table(u'shop_taxclass')

        # Deleting model 'Order'
        db.delete_table(u'shop_order')

        # Deleting model 'OrderItem'
        db.delete_table(u'shop_orderitem')

        # Deleting model 'OrderStatus'
        db.delete_table(u'shop_orderstatus')

        # Deleting model 'OrderPayment'
        db.delete_table(u'shop_orderpayment')


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
            'Meta': {'ordering': "['name']", 'object_name': 'Category'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
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
            'Meta': {'ordering': "['-date_created']", 'unique_together': "(('name', 'store'),)", 'object_name': 'Product'},
            '_unit_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '10'}),
            'capacity_per_month': ('django.db.models.fields.IntegerField', [], {}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['imly.Category']"}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_bestseller': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lead_time': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'product_image': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['imly.Store']"}),
            'tax_class': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shop.TaxClass']"}),
            'tax_included': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'imly.store': {
            'Meta': {'ordering': "['-date_created']", 'object_name': 'Store'},
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
        },
        u'shop.order': {
            'Meta': {'object_name': 'Order'},
            '_order_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'billing_address': ('django.db.models.fields.TextField', [], {}),
            'billing_city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'billing_company': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'billing_country': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'billing_first_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'billing_last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'billing_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'confirmed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'data': ('plata.fields.JSONField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items_discount': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '18', 'decimal_places': '10'}),
            'items_subtotal': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '18', 'decimal_places': '10'}),
            'items_tax': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '18', 'decimal_places': '10'}),
            'language_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'paid': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '18', 'decimal_places': '10'}),
            'shipping_address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'shipping_city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'shipping_company': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'shipping_cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'shipping_country': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'shipping_discount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            'shipping_first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'shipping_last_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'shipping_method': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'shipping_same_as_billing': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'shipping_tax': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '18', 'decimal_places': '10'}),
            'shipping_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'}),
            'total': ('django.db.models.fields.DecimalField', [], {'default': "'0.00'", 'max_digits': '18', 'decimal_places': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'orders'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'shop.orderitem': {
            'Meta': {'ordering': "('product',)", 'unique_together': "(('order', 'product'),)", 'object_name': 'OrderItem'},
            '_line_item_discount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '10', 'blank': 'True'}),
            '_line_item_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '18', 'decimal_places': '10'}),
            '_line_item_tax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '18', 'decimal_places': '10'}),
            '_unit_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '10'}),
            '_unit_tax': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '10'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'data': ('plata.fields.JSONField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_sale': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': u"orm['shop.Order']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['imly.Product']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'sku': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'tax_class': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shop.TaxClass']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        },
        u'shop.orderpayment': {
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'OrderPayment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'authorized': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'data': ('plata.fields.JSONField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': u"orm['shop.Order']"}),
            'payment_method': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'payment_module': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'payment_module_key': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'shop.orderstatus': {
            'Meta': {'ordering': "('created', 'id')", 'object_name': 'OrderStatus'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'statuses'", 'to': u"orm['shop.Order']"}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '20'})
        },
        u'shop.taxclass': {
            'Meta': {'ordering': "['-priority']", 'object_name': 'TaxClass'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'priority': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        }
    }

    complete_apps = ['shop']