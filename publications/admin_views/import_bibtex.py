__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

import string
import re

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from publications.bibtex import parse
from publications.forms import ImportBibtexForm
from publications.models import Publication, Type


def import_bibtex(request):
    tmpl = 'admin/publications/import_bibtex.html'
    title = 'Import BibTex'
    if request.method != 'POST':
        return render(request, tmpl, {
            'title': title,
            'form': ImportBibtexForm(),
        })

    form = ImportBibtexForm(request.POST)
    if form.is_valid():
        s = 's' if len(publications) > 1 else ''
        msg = 'Successfully added %d publication%s.' % (len(publications), s)
        messages.info(request, msg)
        return HttpResponseRedirect('../')

    else:
        return render(request, tmpl, {
            'title': title,
            'form': form,
        })

import_bibtex = staff_member_required(import_bibtex)
