from rest_framework import serializers

from .models import (
    ETDRSGridAnnotation,
    MeasurementAnnotation,
    BooleanClassificationAnnotation,
    PolygonAnnotationSet,
    SinglePolygonAnnotation,
    LandmarkAnnotationSet,
    SingleLandmarkAnnotation,
    ImageQualityAnnotation,
    ImagePathologyAnnotation,
    RetinaImagePathologyAnnotation,
    ImageTextAnnotation,
)
from .validators import validate_grader_is_current_retina_user


class AbstractAnnotationSerializer(serializers.ModelSerializer):
    def validate_grader(self, value):
        """
        Validate that grader is the user creating the object for retina_graders group
        """
        validate_grader_is_current_retina_user(value, self.context)
        return value

    class Meta:
        abstract = True


class AbstractSingleAnnotationSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        Validate that the user that is creating this object equals the
        annotation_set.grader for retina_graders
        """
        if data.get("annotation_set") is None:
            return data

        grader = data["annotation_set"].grader
        validate_grader_is_current_retina_user(grader, self.context)
        return data

    class Meta:
        abstract = True


class ETDRSGridAnnotationSerializer(AbstractAnnotationSerializer):
    class Meta:
        model = ETDRSGridAnnotation
        fields = ("id", "grader", "created", "image", "fovea", "optic_disk")


class MeasurementAnnotationSerializer(AbstractAnnotationSerializer):
    class Meta:
        model = MeasurementAnnotation
        fields = ("image", "grader", "created", "start_voxel", "end_voxel")


class BooleanClassificationAnnotationSerializer(AbstractAnnotationSerializer):
    class Meta:
        model = BooleanClassificationAnnotation
        fields = ("image", "grader", "created", "name", "value")


class SinglePolygonAnnotationSerializer(AbstractSingleAnnotationSerializer):
    annotation_set = serializers.PrimaryKeyRelatedField(
        queryset=PolygonAnnotationSet.objects.all()
    )

    class Meta:
        model = SinglePolygonAnnotation
        fields = (
            "id",
            "value",
            "annotation_set",
            "created",
            "x_axis_orientation",
            "y_axis_orientation",
            "z",
        )


class PolygonAnnotationSetSerializer(AbstractAnnotationSerializer):
    singlepolygonannotation_set = SinglePolygonAnnotationSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = PolygonAnnotationSet
        fields = (
            "id",
            "image",
            "grader",
            "created",
            "name",
            "singlepolygonannotation_set",
        )


class SingleLandmarkAnnotationSerializer(AbstractSingleAnnotationSerializer):
    class Meta:
        model = SingleLandmarkAnnotation
        fields = ("id", "image", "annotation_set", "landmarks")


class SingleLandmarkAnnotationSerializerNoParent(
    AbstractSingleAnnotationSerializer
):
    class Meta:
        model = SingleLandmarkAnnotation
        fields = ("id", "image", "landmarks")
        extra_kwargs = {"landmarks": {"allow_empty": True}}


class LandmarkAnnotationSetSerializer(AbstractAnnotationSerializer):
    singlelandmarkannotation_set = SingleLandmarkAnnotationSerializerNoParent(
        many=True
    )

    class Meta:
        model = LandmarkAnnotationSet
        fields = ("id", "grader", "created", "singlelandmarkannotation_set")

    def create(self, validated_data):
        sla_data = validated_data.pop("singlelandmarkannotation_set")
        la_set = LandmarkAnnotationSet.objects.create(**validated_data)
        for sla in sla_data:
            SingleLandmarkAnnotation.objects.create(
                annotation_set=la_set, **sla
            )
        return la_set

    def update(self, instance, validated_data):
        sla_data = validated_data.pop("singlelandmarkannotation_set")
        for sla in sla_data:
            sla_image = sla.get("image")
            if (
                sla_image is not None
                and SingleLandmarkAnnotation.objects.filter(
                    image=sla_image, annotation_set=instance
                ).exists()
            ):
                item = SingleLandmarkAnnotation.objects.get(
                    image=sla_image, annotation_set=instance
                )

                new_landmarks = sla.get("landmarks")
                if new_landmarks is not None:
                    if len(new_landmarks) == 0:
                        item.delete()
                    else:
                        item.landmarks = new_landmarks
                        item.save()
            else:
                SingleLandmarkAnnotation.objects.create(
                    annotation_set=instance, **sla
                )
        return instance


class ImageQualityAnnotationSerializer(AbstractAnnotationSerializer):
    class Meta:
        model = ImageQualityAnnotation
        fields = (
            "id",
            "created",
            "grader",
            "image",
            "quality",
            "quality_reason",
        )


class ImagePathologyAnnotationSerializer(AbstractAnnotationSerializer):
    class Meta:
        model = ImagePathologyAnnotation
        fields = ("id", "created", "grader", "image", "pathology")


class RetinaImagePathologyAnnotationSerializer(AbstractAnnotationSerializer):
    class Meta:
        model = RetinaImagePathologyAnnotation
        fields = (
            "id",
            "created",
            "grader",
            "image",
            "amd_present",
            "dr_present",
            "oda_present",
            "myopia_present",
            "cysts_present",
            "other_present",
        )


class ImageTextAnnotationSerializer(AbstractAnnotationSerializer):
    class Meta:
        model = ImageTextAnnotation
        fields = ("id", "created", "grader", "image", "text")
