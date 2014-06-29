from django.forms import ModelForm
from publications.models import Publication

class PublicationAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PublicationAdminForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            required_fields = instance.type.get_bibtex_required_list()
            for field in required_fields:
                self.fields[field].required = True

    class Meta:
        model = Publication
