from django.contrib import admin

from grandchallenge.publications.forms import PublicationForm
from grandchallenge.publications.models import Publication


class PublicationAdmin(admin.ModelAdmin):
    list_display = ["doi", "year", "title", "referenced_by_count"]
    readonly_fields = [
        "title",
        "referenced_by_count",
        "citeproc_json",
        "ama_html",
        "year",
    ]
    form = PublicationForm

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ["doi"]
        else:
            return self.readonly_fields


admin.site.register(Publication, PublicationAdmin)
