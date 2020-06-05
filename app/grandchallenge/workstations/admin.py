from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from grandchallenge.workstations.models import (
    Session,
    Workstation,
    WorkstationImage,
)


class SessionHistoryAdmin(SimpleHistoryAdmin):
    ordering = ("-created",)
    list_display = ["pk", "created", "status", "creator", "region"]
    list_filter = ["status"]
    readonly_fields = [
        "creator",
        "workstation_image",
        "status",
        "logs",
        "region",
    ]
    search_fields = [
        "creator__username",
        "workstation_image__workstation__title",
    ]


admin.site.register(Workstation)
admin.site.register(WorkstationImage)
admin.site.register(Session, SessionHistoryAdmin)
