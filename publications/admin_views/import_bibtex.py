__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

import string
import re

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from publications.helpers import parse
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

    form = ImportBibtexForm(request.POST, request.FILES)
    if form.is_valid():
        s = 's' if form.number_pubs_saved > 1 else ''
        messages.info(request, "%d publication%s successfully created" % (form.number_pubs_saved, s))
        return HttpResponseRedirect('../')

    else:
        return render(request, tmpl, {
            'title': title,
            'form': form,
        })

import_bibtex = staff_member_required(import_bibtex)
