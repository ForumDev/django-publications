from django.utils.translation import ugettext_lazy as _
from django import forms
from django.http import QueryDict
from publications.bibtex import parse, unparse
from publications.helpers import create_publications_from_entries


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
        'not_unique': 'Entry already exists .',
        'fields_needed': 'Author and/or title not present.',
    }

    def clean_bibliography(self, *args, **kwargs):
        data = self.cleaned_data['bibliography']
        if not data:
            return data

        # Try creating a list of publications to add
        entries = parse(data)
        if not entries:
            raise forms.ValidationError('Invalid data')

        publications, errors = create_publications_from_entries(entries)

        # Need to display each list of errors to the user
        display_errors = []
        unparsed = []
        for key, value in errors.iteritems():
            if value:
                display_errors.append(
                    forms.ValidationError(_(self.error_messages[key]), code=key))
                unparsed.append(unparse(value))

        if display_errors:
            mutate = isinstance(self.data, QueryDict)
            if mutate:
                mutable = self.data._mutable
                self.data._mutable = True
            self.data['bibliography'] = '\n'.join(unparsed)
            if mutate:
                self.data._mutable = mutable
            raise forms.ValidationError(display_errors)

        return data
