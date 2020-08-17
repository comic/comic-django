from crispy_forms.bootstrap import Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Layout, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField
from django.utils.html import format_html
from django_summernote.widgets import SummernoteInplaceWidget
from guardian.shortcuts import get_objects_for_user

from grandchallenge.algorithms.models import Algorithm
from grandchallenge.core.validators import ExtensionValidator
from grandchallenge.core.widgets import JSONEditorWidget
from grandchallenge.evaluation.models import (
    Config,
    EXTRA_RESULT_COLUMNS_SCHEMA,
    Method,
    Submission,
)
from grandchallenge.jqfileupload.widgets import uploader
from grandchallenge.jqfileupload.widgets.uploader import UploadedAjaxFileList
from grandchallenge.subdomains.utils import reverse

submission_options = (
    "submission_page_html",
    "daily_submission_limit",
    "allow_submission_comments",
    "supplementary_file_choice",
    "supplementary_file_label",
    "supplementary_file_help_text",
    "publication_url_choice",
)

scoring_options = (
    "score_title",
    "score_jsonpath",
    "score_error_jsonpath",
    "score_default_sort",
    "score_decimal_places",
    "extra_results_columns",
    "scoring_method_choice",
    "auto_publish_new_results",
    "result_display_choice",
)

leaderboard_options = (
    "use_teams",
    "display_submission_comments",
    "show_supplementary_file_link",
    "show_publication_url",
)

result_detail_options = ("display_all_metrics", "submission_join_key")


class ConfigForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            TabHolder(
                Tab("Submission", *submission_options),
                Tab("Scoring", *scoring_options),
                Tab("Leaderboard", *leaderboard_options),
                Tab("Result Detail", *result_detail_options),
            ),
            ButtonHolder(Submit("save", "Save")),
        )

    class Meta:
        model = Config
        fields = (
            *submission_options,
            *scoring_options,
            *leaderboard_options,
            *result_detail_options,
        )
        widgets = {
            "submission_page_html": SummernoteInplaceWidget(),
            "extra_results_columns": JSONEditorWidget(
                schema=EXTRA_RESULT_COLUMNS_SCHEMA
            ),
        }


class MethodForm(forms.ModelForm):
    chunked_upload = UploadedAjaxFileList(
        widget=uploader.AjaxUploadWidget(multifile=False),
        label="Evaluation Method Container",
        validators=[
            ExtensionValidator(allowed_extensions=(".tar", ".tar.gz"))
        ],
        help_text=(
            ".tar.gz archive of the container image produced from the command "
            "'docker save IMAGE | gzip -c > IMAGE.tar.gz'. See "
            "https://docs.docker.com/engine/reference/commandline/save/"
        ),
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.fields["chunked_upload"].widget.user = user

    class Meta:
        model = Method
        fields = ["chunked_upload"]


submission_fields = (
    "comment",
    "supplementary_file",
    "publication_url",
    "chunked_upload",
)


class SubmissionForm(forms.ModelForm):
    chunked_upload = UploadedAjaxFileList(
        widget=uploader.AjaxUploadWidget(multifile=False),
        label="Predictions File",
        validators=[ExtensionValidator(allowed_extensions=(".zip", ".csv"))],
    )
    algorithm = ModelChoiceField(
        queryset=Algorithm.objects.all(),
        help_text=format_html(
            "Select one of your algorithms to submit as a solution to this "
            "challenge. If you have not created your algorithm yet you can "
            "do so <a href={}>on this page</a>.",
            reverse("algorithms:create"),
        ),
    )

    def __init__(
        self,
        *args,
        user,
        algorithm_submission=False,
        display_comment_field=False,
        supplementary_file_choice=Config.OFF,
        supplementary_file_label="",
        supplementary_file_help_text="",
        publication_url_choice=Config.OFF,
        **kwargs,
    ):
        """
        Conditionally render the comment field based on the
        display_comment_field kwarg
        """
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        if not display_comment_field:
            del self.fields["comment"]

        if supplementary_file_label:
            self.fields["supplementary_file"].label = supplementary_file_label

        if supplementary_file_help_text:
            self.fields[
                "supplementary_file"
            ].help_text = supplementary_file_help_text

        if supplementary_file_choice == Config.REQUIRED:
            self.fields["supplementary_file"].required = True
        elif supplementary_file_choice == Config.OFF:
            del self.fields["supplementary_file"]

        if publication_url_choice == Config.REQUIRED:
            self.fields["publication_url"].required = True
        elif publication_url_choice == Config.OFF:
            del self.fields["publication_url"]

        if algorithm_submission:
            del self.fields["chunked_upload"]

            self.fields["algorithm"].queryset = get_objects_for_user(
                user,
                f"{Algorithm._meta.app_label}.change_{Algorithm._meta.model_name}",
                Algorithm,
            ).order_by("title")

            self.helper.layout.append(Submit("save", "Save"))
        else:
            del self.fields["algorithm"]

            self.fields["chunked_upload"].widget.user = user

    def clean_algorithm(self):
        algorithm = self.cleaned_data["algorithm"]

        if algorithm is None:
            raise ValidationError("You must select an algorithm.")
        elif algorithm.latest_ready_image is None:
            raise ValidationError(
                "This algorithm does not have a usable container image. "
                "Please add one and try again."
            )

        return algorithm

    class Meta:
        model = Submission
        fields = submission_fields


class LegacySubmissionForm(SubmissionForm):
    class Meta:
        model = Submission
        fields = ("creator", *submission_fields)
