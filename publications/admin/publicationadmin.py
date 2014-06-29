__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

from django.contrib import admin
from publications.models import CustomLink, CustomFile, Publication
from publications.admin.forms import PublicationAdminForm

class CustomLinkInline(admin.StackedInline):
    model = CustomLink
    extra = 1
    max_num = 5


class CustomFileInline(admin.StackedInline):
    model = CustomFile
    extra = 1
    max_num = 5


class PublicationAdmin(admin.ModelAdmin):
    list_display = ('type', 'first_author', 'title', 'type', 'year', 'journal_or_book_title')
    list_display_links = ('title',)
    change_list_template = 'admin/publications/change_list.html'
    search_fields = ('title', 'journal', 'authors', 'keywords', 'year')
    inlines = [CustomLinkInline, CustomFileInline]

    def change_view(self, request, object_id, *args, **kwargs):
        # Get the required and optional fields
        t = Publication.objects.get(pk=object_id).type
        required_fields = t.get_bibtex_required_list()
        optional_fields = t.get_bibtex_optional_list()

        # Set the fieldsets to optional and required
        self.fieldsets = [
            (None, {'fields':
                ['type', 'title', 'authors', 'year'] + required_fields}),
        ]

        if optional_fields:
            self.fieldsets.append((None, {'fields': optional_fields}))

        # Ensure that none of the optional-applicable-to-all fields are required
        general_fields = [
                'citekey', 'keywords', 'url', 'urldate', 'code', 'pdf', 'doi', 'isbn', 'note', 'external']
        general_fields = [k for k in general_fields if k not in required_fields]

        self.fieldsets.extend([
            (None, {'fields': general_fields}),
            (None, {'fields': ('abstract',)}),
            (None, {'fields': ('image', 'thumbnail')}),
            (None, {'fields': ('lists',)}),
        ])

        # Amended form with required arguments
        self.form = PublicationAdminForm
        self.readonly_fields = ('type',)

        return super(PublicationAdmin, self).change_view(request, object_id, *args, **kwargs)
