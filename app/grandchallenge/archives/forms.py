from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms import (
    Form,
    ModelChoiceField,
    ModelForm,
    ModelMultipleChoiceField,
    TextInput,
)
from django.utils.text import format_lazy
from django_select2.forms import Select2MultipleWidget
from guardian.shortcuts import get_objects_for_user

from grandchallenge.algorithms.models import Algorithm
from grandchallenge.archives.models import Archive, ArchivePermissionRequest
from grandchallenge.cases.models import Image
from grandchallenge.core.forms import (
    PermissionRequestUpdateForm,
    SaveFormInitMixin,
    WorkstationUserFilterMixin,
)
from grandchallenge.core.widgets import MarkdownEditorWidget
from grandchallenge.groups.forms import UserGroupForm
from grandchallenge.reader_studies.models import ReaderStudy
from grandchallenge.subdomains.utils import reverse_lazy


class ArchiveForm(WorkstationUserFilterMixin, SaveFormInitMixin, ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["logo"].required = True
        self.fields["workstation"].required = True
        self.fields["algorithms"].queryset = (
            self.instance.algorithms.all()
            | get_objects_for_user(
                kwargs["user"], "execute_algorithm", Algorithm
            )
        ).distinct()

    class Meta:
        model = Archive
        fields = (
            "title",
            "description",
            "publications",
            "modalities",
            "structures",
            "organizations",
            "logo",
            "social_image",
            "workstation",
            "workstation_config",
            "algorithms",
            "public",
            "detail_page_markdown",
        )
        widgets = {
            "description": TextInput,
            "detail_page_markdown": MarkdownEditorWidget,
            "algorithms": Select2MultipleWidget,
            "publications": Select2MultipleWidget,
            "modalities": Select2MultipleWidget,
            "structures": Select2MultipleWidget,
            "organizations": Select2MultipleWidget,
        }
        help_texts = {
            "workstation_config": format_lazy(
                (
                    "The workstation configuration to use for this archive. "
                    "If a suitable configuration does not exist you can "
                    '<a href="{}">create a new one</a>.'
                ),
                reverse_lazy("workstation-configs:create"),
            ),
        }


class UploadersForm(UserGroupForm):
    role = "uploader"


class UsersForm(UserGroupForm):
    role = "user"

    def add_or_remove_user(self, *, obj):
        super().add_or_remove_user(obj=obj)

        user = self.cleaned_data["user"]

        try:
            permission_request = ArchivePermissionRequest.objects.get(
                user=user, archive=obj
            )
        except ObjectDoesNotExist:
            return

        if self.cleaned_data["action"] == self.REMOVE:
            permission_request.status = ArchivePermissionRequest.REJECTED
        else:
            permission_request.status = ArchivePermissionRequest.ACCEPTED

        permission_request.save()


class ArchivePermissionRequestUpdateForm(PermissionRequestUpdateForm):
    class Meta(PermissionRequestUpdateForm.Meta):
        model = ArchivePermissionRequest


class ArchiveCasesToReaderStudyForm(SaveFormInitMixin, Form):
    reader_study = ModelChoiceField(
        queryset=ReaderStudy.objects.all(), required=True,
    )
    images = ModelMultipleChoiceField(
        queryset=Image.objects.all(),
        required=True,
        widget=Select2MultipleWidget,
    )

    def __init__(self, *args, user, archive, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.archive = archive

        self.fields["reader_study"].queryset = get_objects_for_user(
            self.user,
            f"{ReaderStudy._meta.app_label}.change_{ReaderStudy._meta.model_name}",
            ReaderStudy,
        ).order_by("title")
        self.fields["images"].queryset = Image.objects.filter(
            archive=self.archive
        )
        self.fields["images"].initial = self.fields["images"].queryset

    def clean_reader_study(self):
        reader_study = self.cleaned_data["reader_study"]
        if not self.user.has_perm("change_readerstudy", reader_study):
            raise ValidationError(
                "You do not have permission to change this reader study"
            )
        return reader_study

    def clean_images(self):
        images = self.cleaned_data["images"]
        images = images.filter(archive=self.archive)
        return images

    def clean(self):
        cleaned_data = super().clean()

        cleaned_data["images"] = cleaned_data["images"].exclude(
            readerstudies__in=[cleaned_data["reader_study"]]
        )

        if len(cleaned_data["images"]) == 0:
            raise ValidationError(
                "All of the selected images already exist in that reader study"
            )

        return cleaned_data
