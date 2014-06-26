__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

from django.db import models
from publications.models.orderedmodel import OrderedModel

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
        return [s.strip() for s in self.bibtex_required_fields.split(",")]

    def get_bibtex_optional_list(self):
        return [s.strip() for s in self.bibtex_optional_fields.split(",")] \
                if len(self.bibtex_optional_fields) \
                else []

