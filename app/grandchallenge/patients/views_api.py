from rest_framework.viewsets import ReadOnlyModelViewSet
from grandchallenge.core.utils.query import filter_queryset_fields
from grandchallenge.patients.models import Patient
from grandchallenge.patients.serializers import PatientSerializer


class PatientViewSet(ReadOnlyModelViewSet):
    serializer_class = PatientSerializer

    def get_queryset(self):
        filters = {
            "study__image__worklist": self.request.query_params.get(
                "worklist", None
            ),
            "study__image__files__image_type": self.request.query_params.get(
                "image_type", None
            ),
        }

        queryset = filter_queryset_fields(filters, model=Patient)
        queryset = queryset.distinct()
        return queryset
