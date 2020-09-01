from rest_framework import serializers
from rest_framework.fields import CharField, SerializerMethodField
from rest_framework.relations import HyperlinkedRelatedField

from grandchallenge.algorithms.models import (
    Algorithm,
    AlgorithmImage,
    Job,
)
from grandchallenge.api.swagger import swagger_schema_fields_for_charfield
from grandchallenge.components.serializers import (
    HyperlinkedComponentInterfaceValueSerializer,
)


class AlgorithmSerializer(serializers.ModelSerializer):
    algorithm_container_images = HyperlinkedRelatedField(
        many=True, read_only=True, view_name="api:algorithms-image-detail"
    )
    latest_ready_image = SerializerMethodField()

    class Meta:
        model = Algorithm
        fields = [
            "algorithm_container_images",
            "api_url",
            "description",
            "latest_ready_image",
            "pk",
            "title",
        ]

    def get_latest_ready_image(self, obj: Algorithm):
        """Used by latest_container_image SerializerMethodField."""
        ci = obj.latest_ready_image
        if ci:
            return ci.api_url
        else:
            return None


class AlgorithmImageSerializer(serializers.ModelSerializer):
    algorithm = HyperlinkedRelatedField(
        read_only=True, view_name="api:algorithm-detail"
    )

    class Meta:
        model = AlgorithmImage
        fields = ["pk", "api_url", "algorithm"]


class JobSerializer(serializers.ModelSerializer):
    algorithm_image = HyperlinkedRelatedField(
        queryset=AlgorithmImage.objects.all(),
        view_name="api:algorithms-image-detail",
    )
    status = CharField(source="get_status_display", read_only=True)
    inputs = HyperlinkedComponentInterfaceValueSerializer(many=True)
    outputs = HyperlinkedComponentInterfaceValueSerializer(many=True)

    class Meta:
        model = Job
        fields = [
            "pk",
            "api_url",
            "algorithm_image",
            "inputs",
            "outputs",
            "status",
        ]
        swagger_schema_fields = swagger_schema_fields_for_charfield(
            status=model._meta.get_field("status")
        )
