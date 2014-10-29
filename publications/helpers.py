# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'
__version__ = '1.2.0'

import re
import six
import string
from dateutil import parser as date_parser
from .models import Publication, Type
from django import forms
from django.utils.translation import ugettext_lazy as _


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

# special character mapping
special_chars = (
    (r'\"{a}', 'ä'), (r'{\"a}', 'ä'), (r'\"a', 'ä'), (r'H{a}', 'ä'),
    (r'\"{A}', 'Ä'), (r'{\"A}', 'Ä'), (r'\"A', 'Ä'), (r'H{A}', 'Ä'),
    (r'\"{o}', 'ö'), (r'{\"o}', 'ö'), (r'\"o', 'ö'), (r'H{o}', 'ö'),
    (r'\"{O}', 'Ö'), (r'{\"O}', 'Ö'), (r'\"O', 'Ö'), (r'H{O}', 'Ö'),
    (r'\"{u}', 'ü'), (r'{\"u}', 'ü'), (r'\"u', 'ü'), (r'H{u}', 'ü'),
    (r'\"{U}', 'Ü'), (r'{\"U}', 'Ü'), (r'\"U', 'Ü'), (r'H{U}', 'Ü'),
    (r'{‘a}', 'à'), (r'\‘A', 'À'),
    (r'{‘e}', 'è'), (r'\‘E', 'È'),
    (r'{‘o}', 'ò'), (r'\‘O', 'Ò'),
    (r'{‘u}', 'ù'), (r'\‘U', 'Ù'),
    (r'{’a}', 'á'), (r'\’A', 'Á'),
    (r'{’e}', 'é'), (r'\’E', 'É'),
    (r'{’o}', 'ó'), (r'\’O', 'Ó'),
    (r'{’u}', 'ú'), (r'\’U', 'Ú'),
    (r'\`a', 'à'), (r'\`A', 'À'),
    (r'\`e', 'è'), (r'\`E', 'È'),
    (r'\`u', 'ù'), (r'\`U', 'Ù'),
    (r'\`o', 'ò'), (r'\`O', 'Ò'),
    (r'\^o', 'ô'), (r'\^O', 'Ô'),
    (r'\ss', 'ß'),
    (r'\ae', 'æ'), (r'\AE', 'Æ'),
    (r'\&', '&'))


def get_authors_from_entry(entry):
    authors = entry['author']

    if not (authors[0] == '{' and authors[-1] == '}'):
        authors = authors.split(' and ')
        for i in range(len(authors)):
            author = authors[i].split(',')
            author = [author[-1]] + author[:-1]
            authors[i] = ' '.join(author)
        authors = ', '.join(authors)

    return authors


def get_type_from_entry(entry, types):
    type_id = None
    for t in types:
        if entry['type'] in t.bibtex_type_list:
            type_id = t.id
            break
    return type_id


def rename_entry_key(entry, old_key, new_key):
    if entry.get(old_key):
        entry[new_key] = entry[old_key]
        del entry[old_key]


def create_publications_from_entries(entries, duplicates, save_on_error=True):
    publications = []
    errors = {
        'fields_needed': [],
        'not_unique': [],
        'not_unique_created': [],
        'wrong_type': [],
    }

    types = Type.objects.all()
    citekeys = []

    for entry in entries:

        if 'date' in entry and 'year' not in entry:
            try:
                d = date_parser.parse(entry['date'])
                entry['year'] = d.year
            except ValueError:
                pass

        # Check required fields
        if not ('title' in entry and 'author' in entry):
            errors['fields_needed'].append(entry)
            continue

        # Check for uniqueness
        if Publication.objects.filter(title__iexact=entry['title'], year=entry.get('year', None)).count():
            errors['not_unique_created'].append(entry)
            continue

        authors = get_authors_from_entry(entry)
        type_id = get_type_from_entry(entry, types)
        if type_id is None:
            errors['wrong_type'].append(entry)
            continue

        # Set missing fields
        valid = map(lambda x: x.name, Publication._meta.fields)
        for v in valid:
            if v not in entry and v not in ['number', 'volume', 'urldate', 'year']:
                entry[v] = ''

        # map integer fields to integers
        entry['month'] = MONTHS.get(entry['month'].lower(), 0)
        entry['volume'] = entry.get('volume', None)
        entry['number'] = entry.get('number', None)

        # Rename fields
        rename_entry_key(entry, 'address', 'location')
        rename_entry_key(entry, 'organization', 'institution')
        rename_entry_key(entry, 'key', 'citekey')

        # If URL is provided, ensure it's encoded
        # For now, just replace all spaces with %20
        if entry.get('url'):
            entry['url'] = re.sub(' ', '%20', entry['url'])

        # Strip all non-valid bibtex entries from entry
        invalid = ['type', 'external', 'authors', 'id', 'date']
        entry = dict((k, v) for (k, v) in entry.iteritems() if k in valid and k not in invalid)

        # Generate a cite key if not defined
        if not entry.get('citekey'):
            aut_list = authors.split(',')[0].split('. ')
            aut_list.reverse()
            entry['citekey'] = aut_list[0] + entry['year']

        # If we're parsing a long list and the key has already been found,
        # continue
        if entry['citekey'] in duplicates:
            errors['not_unique'].append(entry['citekey'])
            continue

        # Ensure that the cite key is unique and if not append letters
        citekey = entry['citekey']
        pub_count = citekeys.count(entry['citekey'])
        pub_count += Publication.objects.filter(citekey__startswith=entry['citekey']).count()
        if pub_count:
            citekeys.append(citekey)
            entry['citekey'] += string.lowercase[pub_count]

        # add publication
        citekeys.append(entry['citekey'])
        publications.append(Publication(
            type_id=type_id,
            authors=authors,
            external=False,
            **entry
        ))

    # Save publications
    if save_on_error:
        Publication.objects.bulk_create(publications)

    return publications, errors


def parse(string):
    """
    Takes a string in BibTex format and returns a list of BibTex entries, where
    each entry is a dictionary containing the entries' key-value pairs.

    @type  string: string
    @param string: bibliography in BibTex format

    @rtype: list
    @return: a list of dictionaries representing a bibliography
    """

    # bibliography
    bib = []

    # make sure we are dealing with unicode strings
    if not isinstance(string, six.text_type):
        string = string.decode('utf-8')

    # replace special characters
    for key, value in special_chars:
        string = string.replace(key, value)

    # split into BibTex entries
    entries = re.findall(r'(?u)@(\w+)[ \t]?{[ \t]*([^,\s]*)[ \t]*,?\s*((?:[^=,\s]+\s*\=\s*(?:"[^"]*"|{(?:[^{}]*|{[^{}]*})*}|[^,}]*),?\s*?)+)\s*}', string)

    # Find duplicates
    duplicates = []
    citekeys   = []

    for entry in entries:
        # parse entry
        pairs = re.findall(r'(?u)([^=,\s]+)\s*\=\s*("[^"]*"|{(?:[^{}]*|{[^{}]*})*}|[^,]*)', entry[2])

        # add to bibliography
        bib.append({'type': entry[0].lower(), 'key': entry[1]})

        if entry[1] in citekeys:
            duplicates.append(entry[1])

        citekeys.append(entry[1])

        for key, value in pairs:
            # If there's a type defined, it will mess things up so ignore it
            if key == 'type':
                continue

            # post-process key and value
            key = key.lower()
            if value and value[0] == '"' and value[-1] == '"':
                value = value[1:-1]
            if value and value[0] == '{' and value[-1] == '}':
                value = value[1:-1]
            if key not in ['booktitle', 'title', 'author']:
                value = value.replace('}', '').replace('{', '')
            if key == 'title' and value[0] == '{' and value[-1] == '}':
                value = value[1:-1]
            value = value.strip()
            value = re.sub(r'\s+', ' ', value)

            # store pair in bibliography
            bib[-1][key] = value

    return bib, duplicates


def unparse(entries):
    es = []
    for entry in entries:
        outline = '@%s{%s,\n\t%s}'
        type = entry.pop('type')
        key = entry.pop('key')
        joined = ',\n\t'.join(['%s = {%s}' % (k, v) for (k, v) in entry.iteritems()])
        es.append(outline % (type, key, joined))
    return '\n'.join(es)
