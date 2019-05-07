from django.views.generic import CreateView, DetailView
from rest_framework.viewsets import ReadOnlyModelViewSet

from grandchallenge.cases.forms import UploadRawImagesForm
from grandchallenge.cases.models import (
    RawImageFile,
    RawImageUploadSession,
    UPLOAD_SESSION_STATE,
    Image,
)
from grandchallenge.cases.serializers import ImageSerializer
from grandchallenge.core.permissions.mixins import UserIsStaffMixin
from grandchallenge.queryset_filter import filter_queryset_fields


class UploadRawFiles(UserIsStaffMixin, CreateView):
    model = RawImageUploadSession
    form_class = UploadRawImagesForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class ShowUploadSessionState(UserIsStaffMixin, DetailView):
    model = RawImageUploadSession

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)

        result["upload_session"] = result["object"]
        result["raw_files"] = RawImageFile.objects.filter(
            upload_session=result["object"]
        ).all()
        result["images"] = Image.objects.filter(origin=result["object"]).all()
        result["process_finished"] = (
            result["object"].session_state == UPLOAD_SESSION_STATE.stopped
        )
        return result


class ImageViewSet(ReadOnlyModelViewSet):
    serializer_class = ImageSerializer

    def get_queryset(self):
        filters = {
            "worklist": self.request.query_params.get(
                "worklist", None
            ),
            "study": self.request.query_params.get(
                "study", None
            ),
        }

        return filter_queryset_fields(filters, model=Image)
