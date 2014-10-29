import re
import string
from dateutil import parser as date_parser
from .models import Publication, Type


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


def create_publications_from_entries(entries, save_on_error=True):
    publications = []
    errors = {
        'fields_needed': [],
        'not_unique': [],
        'wrong_type': [],
    }

    types = Type.objects.all()

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
            errors['not_unique'].append(entry)
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

        # Generate a cite key if not defined
        if not entry.get('citekey'):
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
        invalid = ['type', 'external', 'authors', 'id', 'date']
        entry = dict((k, v) for (k, v) in entry.iteritems() if k in valid and k not in invalid)

        # add publication
        publications.append(Publication(
            type_id=type_id,
            authors=authors,
            external=False,
            **entry
        ))

    # Save publications
    if save_on_error:
        for publication in publications:
            publication.save()

    return publications, errors
