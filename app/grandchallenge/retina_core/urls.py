from django.urls import include, path

from grandchallenge.retina_core.views import ThumbnailView

app_name = "retina"
urlpatterns = [
    path("api/", include("grandchallenge.retina_api.urls", namespace="api")),
    path(
        "retina_importers/",
        include("grandchallenge.retina_importers.urls", namespace="importers"),
    ),
    path(
        "image/thumbnail/<uuid:image_id>/",
        ThumbnailView.as_view(),
        name="image-thumbnail",
    ),
]
