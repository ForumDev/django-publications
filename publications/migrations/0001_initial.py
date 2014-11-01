# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Type'
        db.create_table(u'publications_type', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('bibtex_types', self.gf('django.db.models.fields.CharField')(default='article', max_length=256)),
            ('bibtex_required_fields', self.gf('django.db.models.fields.TextField')()),
            ('bibtex_optional_fields', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'publications', ['Type'])

        # Adding model 'List'
        db.create_table(u'publications_list', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('list', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'publications', ['List'])

        # Adding model 'Style'
        db.create_table(u'publications_style', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
        ))
        db.send_create_signal(u'publications', ['Style'])

        # Adding model 'StyleTemplate'
        db.create_table(u'publications_styletemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('style', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['publications.Style'])),
            ('bibtype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['publications.Type'])),
            ('template', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'publications', ['StyleTemplate'])

        # Adding model 'Publication'
        db.create_table(u'publications_publication', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['publications.Type'])),
            ('citekey', self.gf('django.db.models.fields.CharField')(max_length=512, unique=True, null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('authors', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('year', self.gf('django.db.models.fields.PositiveIntegerField')(max_length=4, null=True, blank=True)),
            ('month', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('journal', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('book_title', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('publisher', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('institution', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('volume', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('edition', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('series', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('pages', self.gf('publications.fields.PagesField')(max_length=32, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('keywords', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=1000, blank=True)),
            ('urldate', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('pdf', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('doi', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('external', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('abstract', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('isbn', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('issn', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
        ))
        db.send_create_signal(u'publications', ['Publication'])

        # Adding M2M table for field lists on 'Publication'
        m2m_table_name = db.shorten_name(u'publications_publication_lists')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('publication', models.ForeignKey(orm[u'publications.publication'], null=False)),
            ('list', models.ForeignKey(orm[u'publications.list'], null=False))
        ))
        db.create_unique(m2m_table_name, ['publication_id', 'list_id'])

        # Adding model 'CustomFile'
        db.create_table(u'publications_customfile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('publication', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['publications.Publication'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'publications', ['CustomFile'])

        # Adding model 'CustomLink'
        db.create_table(u'publications_customlink', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('publication', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['publications.Publication'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal(u'publications', ['CustomLink'])


    def backwards(self, orm):
        # Deleting model 'Type'
        db.delete_table(u'publications_type')

        # Deleting model 'List'
        db.delete_table(u'publications_list')

        # Deleting model 'Style'
        db.delete_table(u'publications_style')

        # Deleting model 'StyleTemplate'
        db.delete_table(u'publications_styletemplate')

        # Deleting model 'Publication'
        db.delete_table(u'publications_publication')

        # Removing M2M table for field lists on 'Publication'
        db.delete_table(db.shorten_name(u'publications_publication_lists'))

        # Deleting model 'CustomFile'
        db.delete_table(u'publications_customfile')

        # Deleting model 'CustomLink'
        db.delete_table(u'publications_customlink')


    models = {
        u'publications.customfile': {
            'Meta': {'object_name': 'CustomFile'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publication': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['publications.Publication']"})
        },
        u'publications.customlink': {
            'Meta': {'object_name': 'CustomLink'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publication': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['publications.Publication']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'publications.list': {
            'Meta': {'ordering': "('list',)", 'object_name': 'List'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'list': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'publications.publication': {
            'Meta': {'ordering': "['-year', '-month', '-id']", 'object_name': 'Publication'},
            'abstract': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'authors': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'book_title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'citekey': ('django.db.models.fields.CharField', [], {'max_length': '512', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'doi': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'edition': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'external': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'institution': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'isbn': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'issn': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'journal': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'lists': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['publications.List']", 'symmetrical': 'False', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pages': ('publications.fields.PagesField', [], {'max_length': '32', 'blank': 'True'}),
            'pdf': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'series': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['publications.Type']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '1000', 'blank': 'True'}),
            'urldate': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'volume': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'})
        },
        u'publications.style': {
            'Meta': {'object_name': 'Style'},
            'bibtype': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['publications.Type']", 'through': u"orm['publications.StyleTemplate']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'})
        },
        u'publications.styletemplate': {
            'Meta': {'object_name': 'StyleTemplate'},
            'bibtype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['publications.Type']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'style': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['publications.Style']"}),
            'template': ('django.db.models.fields.TextField', [], {})
        },
        u'publications.type': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Type'},
            'bibtex_optional_fields': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'bibtex_required_fields': ('django.db.models.fields.TextField', [], {}),
            'bibtex_types': ('django.db.models.fields.CharField', [], {'default': "'article'", 'max_length': '256'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['publications']