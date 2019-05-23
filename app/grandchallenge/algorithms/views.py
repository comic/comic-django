import logging

from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, CreateView, DetailView

from grandchallenge.algorithms.forms import AlgorithmForm
from grandchallenge.algorithms.models import Algorithm
from grandchallenge.cases.forms import UploadRawImagesForm
from grandchallenge.cases.models import RawImageUploadSession
from grandchallenge.core.permissions.mixins import UserIsStaffMixin
from grandchallenge.subdomains.utils import reverse

logger = logging.getLogger(__name__)


class AlgorithmList(UserIsStaffMixin, ListView):
    model = Algorithm


class AlgorithmCreate(UserIsStaffMixin, CreateView):
    model = Algorithm
    form_class = AlgorithmForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        uploaded_file = form.cleaned_data["chunked_upload"][0]
        form.instance.staged_image_uuid = uploaded_file.uuid
        return super().form_valid(form)


class AlgorithmDetail(UserIsStaffMixin, DetailView):
    model = Algorithm


class AlgorithmExecutionSessionCreate(
    UserIsStaffMixin, SuccessMessageMixin, CreateView
):
    model = RawImageUploadSession
    form_class = UploadRawImagesForm
    template_name = "algorithms/algorithm_execution_session_create.html"
    success_message = (
        "Your images have been uploaded, "
        "please check back here to see the processing status."
    )

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.algorithm = Algorithm.objects.get(
            slug=self.kwargs["slug"]
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "algorithms:detail", kwargs={"slug": self.kwargs["slug"]}
        )
