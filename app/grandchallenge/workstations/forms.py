from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from dal import autocomplete
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import (
    ModelForm,
    Form,
    ModelChoiceField,
    ChoiceField,
    HiddenInput,
)
from guardian.utils import get_anonymous_user

from grandchallenge.core.validators import ExtensionValidator
from grandchallenge.jqfileupload.widgets import uploader
from grandchallenge.core.forms import SaveFormInitMixin
from grandchallenge.workstations.models import Workstation, WorkstationImage


class WorkstationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout.append(Submit("save", "Save"))

    class Meta:
        model = Workstation
        fields = ("title", "logo", "description")


workstation_image_upload_widget = uploader.AjaxUploadWidget(
    ajax_target_path="ajax/workstation-image-upload/", multifile=False
)


class WorkstationImageForm(ModelForm):
    chunked_upload = uploader.UploadedAjaxFileList(
        widget=workstation_image_upload_widget,
        label="Workstation Image",
        validators=[
            ExtensionValidator(allowed_extensions=(".tar", ".tar.gz"))
        ],
        help_text=(
            ".tar.gz archive of the container image produced from the command "
            "'docker save IMAGE | gzip -c > IMAGE.tar.gz'. See "
            "https://docs.docker.com/engine/reference/commandline/save/"
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)

    class Meta:
        model = WorkstationImage
        fields = (
            "initial_path",
            "http_port",
            "websocket_port",
            "chunked_upload",
        )


class UserGroupForm(SaveFormInitMixin, Form):
    ADD = "ADD"
    REMOVE = "REMOVE"
    CHOICES = ((ADD, "Add"), (REMOVE, "Remove"))
    user = ModelChoiceField(
        queryset=get_user_model().objects.all().order_by("username"),
        help_text="Select a user that will be added to the group",
        required=True,
        widget=autocomplete.ModelSelect2(
            url="workstations:users-autocomplete",
            attrs={
                "data-placeholder": "Search for a user ...",
                "data-minimum-input-length": 3,
                "data-theme": settings.CRISPY_TEMPLATE_PACK,
            },
        ),
    )
    action = ChoiceField(
        choices=CHOICES, required=True, widget=HiddenInput(), initial=ADD
    )

    def clean_user(self):
        user = self.cleaned_data["user"]
        if user == get_anonymous_user():
            raise ValidationError("You cannot add this user!")
        return user

    def add_or_remove_user(self, *, workstation):
        if self.cleaned_data["action"] == self.ADD:
            getattr(workstation, f"add_{self.role}")(self.cleaned_data["user"])
        elif self.cleaned_data["action"] == self.REMOVE:
            getattr(workstation, f"remove_{self.role}")(
                self.cleaned_data["user"]
            )


class EditorsForm(UserGroupForm):
    role = "editor"
