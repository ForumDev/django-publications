import logging
from django.test import TestCase
from publications.forms import ImportBibtexForm
from publications.models import Publication


logging.disable(logging.CRITICAL)


valid1 = """
@book{Swyngedouw2004,
pagetotal = {234},
shorttitle = {{Social Power and the Urbanization of Water}},
title = {{Social Power and the Urbanization of Water: Flows of Power}},
publisher = {{Oxford University Press}},
author = {Swyngedouw, Erik},
date = {2004},
year = {2004},
langid = {english},
keywords = {Political Science / Public Policy / City Planning \& Urban Development,Political Science / Public Policy / Social Policy}
}
"""

valid2 = """
@article{Kaika2000,
pages = {120-138},
shorttitle = {{Fetishizing the modern city}},
title = {{Fetishizing the modern city: the phantasmagoria of urban technological networks}},
url = {http://onlinelibrary.wiley.com/doi/10.1111/1468-2427.00239/abstract},
volume = {{24}},
number = {1},
journaltitle = {{International Journal of Urban and Regional Research}},
author = {Kaika, Maria and Swyngedouw, Erik},
urldate = {2014-10-07},
date = {2000-03-01},
year = {2000},
langid = {english},
file = {Kaika_Swyngedouw_2000_Fetishizing the modern city.pdf:/home/caz/Dropbox/Auckland/Kaika_Swyngedouw_2000_Fetishizing the modern city.pdf:application/pdf}
}
"""

invalid_type = """
@invalid{Seminario2011,
    file = {Seminario_2011_Gendered Political Ecology of Coffee and Maize Agro-Ecosystems.pdf:/home/caz/Dropbox/Auckland/Seminario_2011_Gendered Political Ecology of Coffee and Maize Agro-Ecosystems.pdf:application/pdf},
    author = {Seminario, Bruno Ricardo Portillo},
    url = {http://lup.lub.lu.se/record/1962174/file/1962210.pdf},
    title = {Gendered Political Ecology of Coffee and Maize Agro-Ecosystems},
    date = {2011},
    year = {2011},
    urldate = {2014-10-16},
    institution = {Lund University}}
"""


class ImportBibtexTests(TestCase):
    def bib_form(self, data):
        return ImportBibtexForm(data={
            'bibliography': data,
        })

    def test_import_bibliography_nonsense(self):
        form = ImportBibtexForm(data={
            'bibliography': 'arst'
        })
        self.assertFalse(form.is_valid())

    def test_import_bibliography_one_entry(self):
        form = self.bib_form(valid1)
        self.assertTrue(form.is_valid())

        # Assert one publication created
        self.assertEqual(Publication.objects.all().count(), 1)
        p = Publication.objects.get(pk=1)
        self.assertEqual(p.title, "Social Power and the Urbanization of Water: Flows of Power")
        self.assertEqual(p.authors, "E. Swyngedouw")

    def test_import_bibliography_multiple_entries(self):
        form = self.bib_form(valid1 + valid2)
        self.assertTrue(form.is_valid())
        self.assertEqual(Publication.objects.all().count(), 2)

    def test_import_bibliography_invalid(self):
        form = self.bib_form(invalid_type)
        self.assertFalse(form.is_valid())
        self.assertIn('bibliography', form.errors.keys())
        self.assertIn(form.error_messages['wrong_type'], form.errors.values()[0])

    def test_import_bibliography_multiple_one_invalid(self):
        form = self.bib_form(invalid_type + valid1)
        self.assertFalse(form.is_valid())
        self.assertIn('bibliography', form.errors.keys())
        self.assertIn(form.error_messages['wrong_type'], form.errors.values()[0])
        self.assertNotIn('Swyngedouw', form.data['bibliography'])
