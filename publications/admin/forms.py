from django.forms import ModelForm
from publications.models import Publication

class PublicationAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PublicationAdminForm, self).__init__(*args, **kwargs)
        t = kwargs['instance'].type
        required_fields = t.get_bibtex_required_list()
        for field in required_fields:
            self.fields[field].required = True

    class Meta:
        model = Publication
