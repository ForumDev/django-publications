# -*- coding: utf-8 -*-

__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

import calendar
import warnings

from django.db import models
from django.dispatch import receiver
from django.forms import model_to_dict
from django.template import Template, Context

from django.utils.http import urlquote_plus
from django.contrib.sites.models import Site
from publications.fields import PagesField
from string import ascii_uppercase



from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Max, Min, F
from django.utils.translation import ugettext as _

class OrderedModel(models.Model):
    """
    An abstract model that allows objects to be ordered relative to each other.
    Provides an ``order`` field.
    """

    order = models.PositiveIntegerField(editable=False, db_index=True)
    order_with_respect_to = None

    class Meta:
        abstract = True
        ordering = ('order',)

    def _get_order_with_respect_to(self):
        return getattr(self, self.order_with_respect_to)

    def _valid_ordering_reference(self, reference):
        return self.order_with_respect_to is None or (
            self._get_order_with_respect_to() == reference._get_order_with_respect_to()
        )

    def get_ordering_queryset(self, qs=None):
        qs = qs or self._default_manager.all()
        order_with_respect_to = self.order_with_respect_to
        if order_with_respect_to:
            value = self._get_order_with_respect_to()
            qs = qs.filter((order_with_respect_to, value))
        return qs

    def save(self, *args, **kwargs):
        if not self.id:
            c = self.get_ordering_queryset().aggregate(Max('order')).get('order__max')
            self.order = 0 if c is None else c + 1
        super(OrderedModel, self).save(*args, **kwargs)

    def _move(self, up, qs=None):
        qs = self.get_ordering_queryset(qs)

        if up:
            qs = qs.order_by('-order').filter(order__lt=self.order)
        else:
            qs = qs.filter(order__gt=self.order)
        try:
            replacement = qs[0]
        except IndexError:
            # already first/last
            return
        self.order, replacement.order = replacement.order, self.order
        self.save()
        replacement.save()

    def move(self, direction, qs=None):
        warnings.warn(
            _("The method move() is deprecated and will be removed in the next release."),
            DeprecationWarning
        )
        if direction == 'up':
            self.up()
        else:
            self.down()

    def move_down(self):
        """
        Move this object down one position.
        """
        warnings.warn(
            _("The method move_down() is deprecated and will be removed in the next release. Please use down() instead!"),
            DeprecationWarning
        )
        return self.down()

    def move_up(self):
        """
        Move this object up one position.
        """
        warnings.warn(
            _("The method move_up() is deprecated and will be removed in the next release. Please use up() instead!"),
            DeprecationWarning
        )
        return self.up()

    def swap(self, qs):
        """
        Swap the positions of this object with a reference object.
        """
        try:
            replacement = qs[0]
        except IndexError:
            # already first/last
            return
        if not self._valid_ordering_reference(replacement):
            raise ValueError(
                "%r can only be swapped with instances of %r which %s equals %r." % (
                    self, self.__class__, self.order_with_respect_to,
                    self._get_order_with_respect_to()
                )
            )
        self.order, replacement.order = replacement.order, self.order
        self.save()
        replacement.save()

    def up(self):
        """
        Move this object up one position.
        """
        self.swap(self.get_ordering_queryset().filter(order__lt=self.order).order_by('-order'))

    def down(self):
        """
        Move this object down one position.
        """
        self.swap(self.get_ordering_queryset().filter(order__gt=self.order))

    def to(self, order):
        """
        Move object to a certain position, updating all affected objects to move accordingly up or down.
        """
        if order is None or self.order == order:
            # object is already at desired position
            return
        qs = self.get_ordering_queryset()
        if self.order > order:
            qs.filter(order__lt=self.order, order__gte=order).update(order=F('order') + 1)
        else:
            qs.filter(order__gt=self.order, order__lte=order).update(order=F('order') - 1)
        self.order = order
        self.save()

    def above(self, ref):
        """
        Move this object above the referenced object.
        """
        if not self._valid_ordering_reference(ref):
            raise ValueError(
                "%r can only be moved above instances of %r which %s equals %r." % (
                    self, self.__class__, self.order_with_respect_to,
                    self._get_order_with_respect_to()
                )
            )
        if self.order == ref.order:
            return
        if self.order > ref.order:
            o = ref.order
        else:
            o = self.get_ordering_queryset().filter(order__lt=ref.order).aggregate(Max('order')).get('order__max') or 0
        self.to(o)

    def below(self, ref):
        """
        Move this object below the referenced object.
        """
        if not self._valid_ordering_reference(ref):
            raise ValueError(
                "%r can only be moved below instances of %r which %s equals %r." % (
                    self, self.__class__, self.order_with_respect_to,
                    self._get_order_with_respect_to()
                )
            )
        if self.order == ref.order:
            return
        if self.order > ref.order:
            o = self.get_ordering_queryset().filter(order__gt=ref.order).aggregate(Min('order')).get('order__min') or 0
        else:
            o = ref.order
        self.to(o)

    def top(self):
        """
        Move this object to the top of the ordered stack.
        """
        o = self.get_ordering_queryset().aggregate(Min('order')).get('order__min')
        self.to(o)

    def bottom(self):
        """
        Move this object to the bottom of the ordered stack.
        """
        o = self.get_ordering_queryset().aggregate(Max('order')).get('order__max')
        self.to(o)

class Type(OrderedModel):
    class Meta:
        ordering = ('order',)
        verbose_name_plural = '  Types'

    type = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    bibtex_types = models.CharField(max_length=256, default='article',
            verbose_name='BibTex types',
            help_text='Possible BibTex types, separated by comma.')
    bibtex_required_fields = models.TextField(
            verbose_name='BibTeX required fields',
            help_text='Required fields (not including title, author, year)',
    )
    bibtex_optional_fields = models.TextField(
            blank=True, null=True,
            verbose_name='BibTeX optional fields',
            help_text='Optional fields (not including title, author, year)',
    )

    hidden = models.BooleanField(
        default=False,
        help_text='Hide publications from main view.')

    def __unicode__(self):
        return self.type


    def __init__(self, *args, **kwargs):
        OrderedModel.__init__(self, *args, **kwargs)

        self.bibtex_types = self.bibtex_types.replace('@', '')
        self.bibtex_types = self.bibtex_types.replace(';', ',')
        self.bibtex_types = self.bibtex_types.replace('and', ',')
        self.bibtex_type_list = [s.strip().lower()
            for s in self.bibtex_types.split(',')]
        self.bibtex_types = ', '.join(self.bibtex_type_list)
        self.bibtex_type = self.bibtex_type_list[0]

    def get_bibtex_required_list(self):
        return [s.strip() for s in self.bibtex_required_fields.split(",")] \
                if self.bibtex_optional_fields \
                else []

    def get_bibtex_optional_list(self):
        return [s.strip() for s in self.bibtex_optional_fields.split(",")] \
                if self.bibtex_optional_fields \
                else []

class List(models.Model):
    """
    Model representing a list of publications.
    """

    class Meta:
        ordering = ('list',)
        verbose_name_plural = 'Lists'

    list = models.CharField(max_length=128)
    description = models.CharField(max_length=128)

    def __unicode__(self):
        return self.list
    

class Style(models.Model):
    """
    When Style created, need to create x StyleTemplate with FK to Type and FK to Style.
    When Type created, need to create new StyleTemplate for each Style.
    StyleTemplate should not ever be created manually.

    """
    name  = models.CharField(max_length=256, unique=True)
    bibtype = models.ManyToManyField('Type', through='StyleTemplate')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        from publications.models import Type
        create_style_templates = self.pk is None
        super(Style, self).save(*args, **kwargs)
        if create_style_templates:
            # Look up Types and create a StyleTemplate for each
            types = Type.objects.all()
            for t in types:
                StyleTemplate(
                        style=self,
                        bibtype=t,
                        template="",
                ).save()

@receiver(models.signals.post_save, sender='publications.Type')
def post_save_type(sender, instance, created, raw, **kwargs):
    # If loading models from a fixture, ignore because the db will get messed up
    # Similarly, if the type has already been created we don't need to do this
    if raw or not created: return

    # For each existing style, create a corresponding StyleTemplate to this Type
    styles = Style.objects.all()
    for s in styles:
        StyleTemplate(
                style=s,
                bibtype=instance,
                template="",
        ).save()
        
class StyleTemplate(models.Model):
    style = models.ForeignKey('Style')
    bibtype = models.ForeignKey('Type')
    template = models.TextField()

    def __unicode__(self):
        return self.bibtype.type

    def format(self, publication):
        context = model_to_dict(publication)
        context['authors'] = self.format_authors(publication)

        t = self.template
        if context.get('url'):
            t = '<a href="{{ url }}">' + t + '</a>'

        t = Template(t)
        c = Context(context)
        return t.render(c)

    def format_authors(self, publication):
        names = publication.authors_list
        lnames = len(names)
        if lnames >= 4:
            return '{} et al.'.format(names[0])
        if lnames > 1:
            return '{} and {}'.format(', '.join(names[:-1]), names[-1])
        return names[0]


class Publication(models.Model):
    """
    Model representing a publication.
    """

    class Meta:
        ordering = ['-year', '-month', '-id']
        verbose_name_plural = ' Publications'

    # names shown in admin area
    MONTH_CHOICES = tuple(enumerate(calendar.month_name[1:], 1))
    MONTH_BIBTEX  = dict(enumerate(calendar.month_abbr[1:], 1))

    type = models.ForeignKey(Type)
    citekey = models.CharField(max_length=512, blank=True, null=True,
        unique=True,
        help_text='BibTex citation key. Leave blank if unsure.')
    title = models.CharField(max_length=512)
    authors = models.CharField(max_length=2048,
        help_text='List of authors separated by commas or <i>and</i>. Wrap with {} to prevent processing.')
    year = models.PositiveIntegerField(max_length=4, blank=True, null=True)
    month = models.IntegerField(choices=MONTH_CHOICES, blank=True, null=True)
    journal = models.CharField(max_length=256, blank=True)
    book_title = models.CharField(max_length=256, blank=True)
    publisher = models.CharField(max_length=256, blank=True)
    institution = models.CharField(max_length=256, blank=True)
    volume = models.IntegerField(blank=True, null=True)
    number = models.IntegerField(blank=True, null=True, verbose_name='Issue number')
    edition = models.CharField(max_length=256, blank=True)
    location = models.CharField(max_length=256, blank=True)
    series = models.CharField(max_length=256, blank=True)
    pages = PagesField(max_length=32, blank=True)
    note = models.TextField(blank=True)
    keywords = models.TextField(blank=True,
        help_text='List of keywords separated by commas.')
    url = models.URLField(blank=True, verbose_name='URL',
        max_length=1000,
        help_text='Link to PDF or journal page.')
    urldate = models.DateField(blank=True, null=True, verbose_name='URL Date',
        help_text='Date url visited',
    )
    code = models.URLField(blank=True,
        help_text='Link to page with code.')
    pdf = models.FileField(upload_to='publications/', verbose_name='PDF', blank=True, null=True)
    image = models.ImageField(upload_to='publications/images/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='publications/thumbnails/', blank=True, null=True)
    doi = models.CharField(max_length=128, verbose_name='DOI', blank=True)
    external = models.BooleanField(
                default=False,
        help_text='If publication was written in another lab, mark as external.')
    abstract = models.TextField(blank=True)
    isbn = models.CharField(max_length=32, verbose_name="ISBN", blank=True,
        help_text='Only for a book.') # A-B-C-D
    issn = models.CharField(max_length=32, verbose_name="ISSN", blank=True) # A-B
    lists = models.ManyToManyField(List, blank=True)

    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)

        # post-process keywords
        self.keywords = self.keywords.replace(';', ',') \
                .replace(', and ', ', ') \
                .replace(',and ', ', ') \
                .replace(' and ', ', ')
        self.keywords = ", ".join([s.strip().lower() for s in self.keywords.split(',')])

        # If the author name is wrapped in brackets, don't process
        if self.authors and self.authors[0] == '{' and self.authors[-1] == '}':
            self.authors_list = [self.authors[1:-1]]
        else:
            # post-process author names
            self.authors = self.authors.replace(', and ', ', ') \
                .replace(',and ', ', ') \
                .replace(' and ', ', ') \
                .replace(';', ',')

            # list of authors
            self.authors_list = [author.strip() for author in self.authors.split(',')]

            # simplified representation of author names
            self.authors_list_simple = []

            # tests if title already ends with a punctuation mark
            self.title_ends_with_punct = self.title[-1] in ['.', '!', '?'] \
                if len(self.title) > 0 else False

            suffixes = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', "Jr.", "Sr."]
            prefixes = ['Dr.']
            prepositions = ['van', 'von', 'der', 'de', 'den']

            # further post-process author names
            for i, author in enumerate(self.authors_list):
                if author == '':
                    continue

                names = author.split(' ')

                # check if last string contains initials
                if (len(names[-1]) <= 3) \
                    and names[-1] not in suffixes \
                    and all(c in ascii_uppercase for c in names[-1]):
                    # turn "Gauss CF" into "C. F. Gauss"
                    names = [c + '.' for c in names[-1]] + names[:-1]

                # number of suffixes
                num_suffixes = 0
                for name in names[::-1]:
                    if name in suffixes:
                        num_suffixes += 1
                    else:
                        break

                # abbreviate names
                for j, name in enumerate(names[:-1 - num_suffixes]):
                    # don't try to abbreviate these
                    if j == 0 and name in prefixes:
                        continue
                    if j > 0 and name in prepositions:
                        continue

                    if (len(name) > 2) or (len(name) and (name[-1] != '.')):
                        k = name.find('-')
                        if 0 < k + 1 < len(name):
                            # take care of dash
                            names[j] = name[0] + '.-' + name[k + 1] + '.'
                        else:
                            names[j] = name[0] + '.'

                if len(names):
                    self.authors_list[i] = ' '.join(names)

                    # create simplified/normalized representation of author name
                    if len(names) > 1:
                        for name in names[0].split('-'):
                            name_simple = self.simplify_name(' '.join([name, names[-1]]))
                            self.authors_list_simple.append(name_simple)
                    else:
                        self.authors_list_simple.append(self.simplify_name(names[0]))

            # list of authors in BibTex format
            self.authors_bibtex = ' and '.join(self.authors_list)

            # overwrite authors string
            if len(self.authors_list) > 2:
                self.authors = ', and '.join([
                    ', '.join(self.authors_list[:-1]),
                    self.authors_list[-1]])
            elif len(self.authors_list) > 1:
                self.authors = ' and '.join(self.authors_list)
            else:
                self.authors = self.authors_list[0]

        # Add magic methods for every style in the database
        def get_format(name):
            def return_format():
                return self.type.styletemplate_set.get(style__name="Harvard").format(self)
            return return_format

        styles = Style.objects.values_list('name', flat=True)
        for s in styles:
            setattr(self, 'format_%s' % s.lower(), get_format(s))

    def __unicode__(self):
        if len(self.title) < 64:
            return self.title
        else:
            index = self.title.rfind(' ', 40, 62)

            if index < 0:
                return self.title[:61] + '...'
            else:
                return self.title[:index] + '...'

    def keywords_escaped(self):
        return [(keyword.strip(), urlquote_plus(keyword.strip()))
            for keyword in self.keywords.split(',')]


    def authors_escaped(self):
        return [(author, author.lower().replace(' ', '+'))
            for author in self.authors_list]


    def key(self):
        # this publication's first author
        author_lastname = self.authors_list[0].split(' ')[-1]

        publications = Publication.objects.filter(
            year=self.year,
            authors__icontains=author_lastname).order_by('month', 'id')

        # character to append to BibTex key
        char = ord('a')

        # augment character for every publication 'before' this publication
        for publication in publications:
            if publication == self:
                break
            if publication.authors_list[0].split(' ')[-1] == author_lastname:
                char += 1

        return self.authors_list[0].split(' ')[-1] + str(self.year) + chr(char)


    def month_bibtex(self):
        return self.MONTH_BIBTEX.get(self.month, '')


    def month_long(self):
        for month_int, month_str in self.MONTH_CHOICES:
            if month_int == self.month:
                return month_str
        return ''


    def first_author(self):
        return self.authors_list[0]


    def journal_or_book_title(self):
        if self.journal:
            return self.journal
        else:
            return self.book_title


    def z3988(self):
        contextObj = ['ctx_ver=Z39.88-2004']

        current_site = Site.objects.get_current()

        rfr_id = current_site.domain.split('.')

        if len(rfr_id) > 2:
            rfr_id = rfr_id[-2]
        elif len(rfr_id) > 1:
            rfr_id = rfr_id[0]
        else:
            rfr_id = ''

        if self.book_title and not self.journal:
            contextObj.append('rft_val_fmt=info:ofi/fmt:kev:mtx:book')
            contextObj.append('rfr_id=info:sid/' + current_site.domain + ':' + rfr_id)
            contextObj.append('rft_id=' + urlquote_plus(self.doi))

            contextObj.append('rft.btitle=' + urlquote_plus(self.title))

            if self.publisher:
                contextObj.append('rft.pub=' + urlquote_plus(self.publisher))

        else:
            contextObj.append('rft_val_fmt=info:ofi/fmt:kev:mtx:journal')
            contextObj.append('rfr_id=info:sid/' + current_site.domain + ':' + rfr_id)
            contextObj.append('rft_id=' + urlquote_plus(self.doi))
            contextObj.append('rft.atitle=' + urlquote_plus(self.title))

            if self.journal:
                contextObj.append('rft.jtitle=' + urlquote_plus(self.journal))

            if self.volume:
                contextObj.append('rft.volume={0}'.format(self.volume))

            if self.pages:
                contextObj.append('rft.pages=' + urlquote_plus(self.pages))

            if self.number:
                contextObj.append('rft.issue={0}'.format(self.number))

        if self.month:
            contextObj.append('rft.date={0}-{1}-1'.format(self.year, self.month))
        else:
            contextObj.append('rft.date={0}'.format(self.year))

        for author in self.authors_list:
            contextObj.append('rft.au=' + urlquote_plus(author))


        if self.isbn:
            contextObj.append('rft.isbn=' + urlquote_plus(self.isbn))
        if self.issn:
            contextObj.append('rft.issn=' + urlquote_plus(self.issn))
            
        return '&'.join(contextObj)


    def clean(self):
        if not self.citekey:
            self.citekey = self.key()

        # remove unnecessary whitespace
        self.title = self.title.strip()
        self.journal = self.journal.strip()
        self.book_title = self.book_title.strip()
        self.publisher = self.publisher.strip()
        self.institution = self.institution.strip()


    @staticmethod
    def simplify_name(name):
        name = name.lower()
        name = name.replace( u'ä', u'ae')
        name = name.replace( u'ö', u'oe')
        name = name.replace( u'ü', u'ue')
        name = name.replace( u'ß', u'ss')
        return name

class CustomFile(models.Model):
    publication = models.ForeignKey(Publication)
    description = models.CharField(max_length=256)
    file = models.FileField(upload_to='publications/')

    def __unicode__(self):
        return self.description

class CustomLink(models.Model):
    publication = models.ForeignKey(Publication)
    description = models.CharField(max_length=256)
    url = models.URLField(verbose_name='URL')

    def __unicode__(self):
        return self.description



        
