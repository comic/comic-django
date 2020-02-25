from django.urls import path

from grandchallenge.algorithms.views import (
    AlgorithmCreate,
    AlgorithmDetail,
    AlgorithmExecutionSessionCreate,
    AlgorithmExecutionSessionDetail,
    AlgorithmImageCreate,
    AlgorithmImageDetail,
    AlgorithmImageUpdate,
    AlgorithmList,
    AlgorithmPermissionRequestCreate,
    AlgorithmPermissionRequestList,
    AlgorithmPermissionRequestUpdate,
    AlgorithmResultUpdate,
    AlgorithmResultsList,
    AlgorithmUpdate,
    AlgorithmUserAutocomplete,
    EditorsUpdate,
    UsersUpdate,
)

app_name = "algorithms"

urlpatterns = [
    path("", AlgorithmList.as_view(), name="list"),
    path("create/", AlgorithmCreate.as_view(), name="create"),
    path(
        "users-autocomplete/",
        AlgorithmUserAutocomplete.as_view(),
        name="users-autocomplete",
    ),
    path("<slug:slug>/", AlgorithmDetail.as_view(), name="detail"),
    path("<slug:slug>/update/", AlgorithmUpdate.as_view(), name="update"),
    path(
        "<slug:slug>/images/create/",
        AlgorithmImageCreate.as_view(),
        name="image-create",
    ),
    path(
        "<slug:slug>/images/<uuid:pk>/",
        AlgorithmImageDetail.as_view(),
        name="image-detail",
    ),
    path(
        "<slug:slug>/images/<uuid:pk>/update/",
        AlgorithmImageUpdate.as_view(),
        name="image-update",
    ),
    path(
        "<slug:slug>/run/",
        AlgorithmExecutionSessionCreate.as_view(),
        name="execution-session-create",
    ),
    path(
        "<slug:slug>/run/<uuid:pk>/",
        AlgorithmExecutionSessionDetail.as_view(),
        name="execution-session-detail",
    ),
    path(
        "<slug:slug>/results/",
        AlgorithmResultsList.as_view(),
        name="results-list",
    ),
    path(
        "<slug:slug>/results/<uuid:pk>/update/",
        AlgorithmResultUpdate.as_view(),
        name="result-update",
    ),
    path(
        "<slug>/editors/update/",
        EditorsUpdate.as_view(),
        name="editors-update",
    ),
    path("<slug>/users/update/", UsersUpdate.as_view(), name="users-update"),
    path(
        "<slug:slug>/permission-requests/",
        AlgorithmPermissionRequestList.as_view(),
        name="permission-request-list",
    ),
    path(
        "<slug:slug>/permission-requests/create/",
        AlgorithmPermissionRequestCreate.as_view(),
        name="permission-request-create",
    ),
    path(
        "<slug:slug>/permission-requests/<int:pk>/update/",
        AlgorithmPermissionRequestUpdate.as_view(),
        name="permission-request-update",
    ),
]
