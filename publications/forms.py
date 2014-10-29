from django.utils.translation import ugettext_lazy as _
from django import forms
from django.http import QueryDict
from publications.helpers import create_publications_from_entries, parse, unparse


class ImportBibtexForm(forms.Form):
    bibliography = forms.CharField(
        widget=forms.Textarea,
        help_text=_('Required keys: title, author and year.'),
        required=False,
    )
    upload = forms.FileField(
        help_text=_('Upload .bib file'),
        required=False,
    )

    error_messages = {
        'wrong_type': 'Type unknown.',
        'not_unique': 'Duplicate keys in bibfile found. Have not been created.',
        'not_unique_created': 'Existing entries already created.',
        'fields_needed': 'Author and/or title not present.',
        'no_entries': 'No valid bib entries found.'
    }

    number_pubs_saved = 0

    def clean_bibliography(self, *args, **kwargs):
        data = self.cleaned_data['bibliography']
        if not data:
            return data

        self._clean_entries('bibliography', data)
        return data

    def clean_upload(self, *args, **kwargs):
        data = self.cleaned_data.get('upload')
        if not data:
            return data

        self._clean_entries('upload', data.read())
        return data

    def _clean_entries(self, field, data):
        # Try creating a list of publications to add
        entries, duplicates = parse(data)
        if not entries:
            raise forms.ValidationError(_(self.error_messages['no_entries']), code='no_entries')

        publications, errors = create_publications_from_entries(entries, duplicates)
        self.number_pubs_saved = len(publications)

        # Work out which ones weren't unique - they are to be displayed
        # separately
        unparsed = []
        is_error = False
        not_unique_created = errors.pop('not_unique_created')
        if not_unique_created:
            is_error = True
            msg = ', '.join([e['key'] for e in not_unique_created])
            self.add_error(field,
                forms.ValidationError(_('%s\n%s' % (self.error_messages['not_unique_created'], msg))))

        not_unique = errors.pop('not_unique')
        if not_unique:
            is_error = True
            msg = ', '.join(list(set(not_unique)))
            self.add_error(field,
                forms.ValidationError(_('%s\n%s' % (self.error_messages['not_unique'], msg))))

        # Need to display each list of errors to the user
        for key, value in errors.iteritems():
            if value:
                is_error = True
                self.add_error('bibliography',
                    forms.ValidationError(_(self.error_messages[key]), code=key))
                unparsed.append(unparse(value))

        if is_error:
            mutate = isinstance(self.data, QueryDict)
            if mutate:
                mutable = self.data._mutable
                self.data._mutable = True
            self.data['bibliography'] = '\n'.join(unparsed)
            if mutate:
                self.data._mutable = mutable
