from django.contrib import admin

from grandchallenge.components.models import (
    ComponentInterface,
    ComponentInterfaceValue,
)


class ComponentInterfaceAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "title",
        "slug",
        "kind",
        "default_value",
        "relative_path",
        "store_in_database",
    )
    readonly_fields = (
        "default_value",
    )


class ComponentInterfaceValueAdmin(admin.ModelAdmin):
    list_display = ("pk", "interface", "value", "file", "image")
    readonly_fields = ("interface", "value", "file", "image")


admin.site.register(ComponentInterface, ComponentInterfaceAdmin)
admin.site.register(ComponentInterfaceValue, ComponentInterfaceValueAdmin)
