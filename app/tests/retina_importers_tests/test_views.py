import pytest
from django.urls import reverse
from rest_framework import status
from .helpers import (
    create_upload_image_test_data,
    remove_test_image,
    batch_test_upload_views,
    create_upload_image_invalid_test_data,
    read_json_file,
)


@pytest.mark.django_db
class TestCustomUploadEndpoints:
    # test functions are added dynamically to this class
    def test_empty(self):
        assert True
    pass


batch_test_data = {
    "upload_image": {
        "data": create_upload_image_test_data(),
        "invalid_data": create_upload_image_invalid_test_data(),
        "url": reverse("upload-image"),
    },
    "upload_etdrs": {
        "data": read_json_file("upload_etdrs_valid_data.json"),
        "invalid_data": read_json_file("upload_etdrs_invalid_data.json"),
        "url": reverse("upload-etdrs-grid-annotation"),
        "annotation_data": True,
    },
    "upload_measurement": {
        "data": read_json_file("upload_measurement_valid_data.json"),
        "invalid_data": read_json_file("upload_measurement_invalid_data.json"),
        "url": reverse("upload-measurement_annotation"),
        "annotation_data": True,
    },
    "upload_boolean_annotation": {
        "data": read_json_file("upload_boolean_valid_data.json"),
        "invalid_data": read_json_file("upload_boolean_invalid_data.json"),
        "url": reverse("upload-boolean-classification-annotation"),
        "annotation_data": True,
    },
    "upload_polygon_annotation": {
        "data": read_json_file("upload_polygon_valid_data.json"),
        "invalid_data": read_json_file("upload_polygon_invalid_data.json"),
        "url": reverse("upload-polygon-annotation"),
        "annotation_data": True,
    },
    "upload_landmark_annotation": {
        "data": read_json_file("upload_registration_valid_data.json"),
        "invalid_data": read_json_file("upload_registration_invalid_data.json"),
        "url": reverse("upload-image-registration-landmarks"),
        "annotation_data": True,
    }
}
batch_test_upload_views(batch_test_data, TestCustomUploadEndpoints)
