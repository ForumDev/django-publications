from django.contrib import admin
from publications.models import Style

class StyleAdminInline(admin.StackedInline):
    model = Style.bibtype.through
    extra = 0
    max_num = 0
    exclude = ('bibtype',)
    verbose_name = ""

    def has_delete_permission(self, request, obj=None):
        return False

class StyleAdmin(admin.ModelAdmin):
    def change_view(self, request, obj_id):
        self.inlines = [StyleAdminInline,]
        return super(StyleAdmin, self).change_view(request, obj_id)
