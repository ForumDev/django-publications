__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

import string
import re

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from publications.bibtex import parse
from publications.models import Publication, Type

# mapping of months
MONTHS = {
    'jan': 1, 'january': 1,
    'feb': 2, 'february': 2,
    'mar': 3, 'march': 3,
    'apr': 4, 'april': 4,
    'may': 5,
    'jun': 6, 'june': 6,
    'jul': 7, 'july': 7,
    'aug': 8, 'august': 8,
    'sep': 9, 'september': 9,
    'oct': 10, 'october': 10,
    'nov': 11, 'november': 11,
    'dec': 12, 'december': 12}

def import_bibtex(request):
    if request.method == 'POST':
        # try to parse BibTex
        bib = parse(request.POST['bibliography'])

        # container for error messages
        errors = {}

        # publication types
        types = Type.objects.all()

        # check for errors
        if not bib:
            if not request.POST['bibliography']:
                errors['bibliography'] = 'This field is required.'

        if not errors:
            publications = []

            # try adding publications
            for entry in bib:
                if 'title' in entry and \
                   'author' in entry and \
                   'year' in entry:

                    # Check the title and year are unique
                    count = Publication.objects.filter(title=entry['title'], year=entry['year']).count()
                    if count:
                        errors['bibliography'] = 'Entry with this title and year already exists'
                        break

                    # parse authors
                    authors = entry['author']

                    if not (authors[0] == '{' and authors[-1] == '}'):
                        authors = authors.split(' and ')
                        for i in range(len(authors)):
                            author = authors[i].split(',')
                            author = [author[-1]] + author[:-1]
                            authors[i] = ' '.join(author)
                        authors = ', '.join(authors)

                    # determine type
                    type_id = None
                    for t in types:
                        if entry['type'] in t.bibtex_type_list:
                            type_id = t.id
                            break
                    if type_id is None:
                        errors['bibliography'] = 'Type "' + entry['type'] + '" unknown.'
                        break

                    # Set missing fields
                    valid = map(lambda x: x.name, Publication._meta.fields)
                    for v in valid:
                        if not v in entry and v not in ['number', 'volume', 'urldate']:
                            entry[v] = ''

                    # map integer fields to integers
                    entry['month'] = MONTHS.get(entry['month'].lower(), 0)
                    entry['volume'] = entry.get('volume', None)
                    entry['number'] = entry.get('number', None)

                    # If address is provided, rename to location
                    if entry.get('address'):
                        entry['location'] = entry['address']
                        del entry['address']

                    # If organization is provided, rename to institution
                    if entry.get('organization'):
                        entry['institution'] = entry['organization']
                        del entry['organization']

                    # If key is provided, rename to citekey
                    if entry.get('key'):
                        entry['citekey'] = entry['key']
                        del entry['key']

                    # Otherwise generate a cite key
                    else:
                        aut_list = authors.split(',')[0].split('. ')
                        aut_list.reverse()
                        entry['citekey'] = aut_list[0] + entry['year']

                    # Ensure that the cite key is unique and if not append letters
                    pubs = Publication.objects.filter(citekey__startswith=entry['citekey']).count()
                    if pubs:
                        entry['citekey'] += string.lowercase[pubs]

                    # If URL is provided, ensure it's encoded
                    # For now, just replace all spaces with %20
                    if entry.get('url'):
                        entry['url'] = re.sub(' ', '%20', entry['url'])

                    # Strip all non-valid bibtex entries from entry
                    invalid = ['type', 'external', 'authors', 'id']
                    entry = dict((k, v) for (k, v) in entry.iteritems() if k in valid and k not in invalid)

                    # add publication
                    publications.append(Publication(
                        type_id=type_id,
                        authors=authors,
                        external=False,
                        **entry
                    ))

                else:
                    errors['bibliography'] = 'Make sure that the keys title, author and year are present.'
                    break

        if not errors and not publications:
            errors['bibliography'] = 'No valid BibTex entries found.'

        if errors:
            # some error occurred
            return render_to_response(
                'admin/publications/import_bibtex.html', {
                    'errors': errors,
                    'title': 'Import BibTex',
                    'types': Type.objects.all(),
                    'request': request},
                RequestContext(request))
        else:
            # save publications
            for publication in publications:
                publication.save()
            else:
                if len(publications) > 1:
                    msg = 'Successfully added ' + str(len(publications)) + ' publications.'
                else:
                    msg = 'Successfully added ' + str(len(publications)) + ' publication.'

            # show message
            messages.info(request, msg)

            # redirect to publication listing
            return HttpResponseRedirect('../')
    else:
        return render_to_response(
            'admin/publications/import_bibtex.html', {
                'title': 'Import BibTex',
                'types': Type.objects.all(),
                'request': request},
            RequestContext(request))

import_bibtex = staff_member_required(import_bibtex)
