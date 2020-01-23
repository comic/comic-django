from os.path import basename

from django.apps import apps
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.management import BaseCommand
from django.utils.module_loading import import_string

"""
profiles.userprofile.mugshot userena.models.upload_to_mugshot
"""


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("field", type=str)
        parser.add_argument("upload_to", type=str)

    def handle(self, *args, **options):
        app_label, model_name, field_name = options["field"].split(".")

        Model = apps.get_model(  # noqa: N806
            app_label=app_label, model_name=model_name
        )
        upload_to = import_string(options["upload_to"])

        objects = Model.objects.all()
        old_storage = FileSystemStorage()

        for obj in objects:
            filefield = getattr(obj, field_name)

            if not filefield:
                print(f"No file for {obj}")
                continue

            filename = basename(filefield.name)
            new_path = upload_to(obj, filename)

            if old_storage.exists(
                filefield.name
            ) and not filefield.storage.exists(new_path):
                print(f"Migrating {filefield.url}")
                filefield.save(
                    filename, File(old_storage.open(filefield.name))
                )

            else:
                print(f"Not migrating {filefield.url}")
