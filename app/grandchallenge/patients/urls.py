from django.urls import path
from grandchallenge.patients import views

app_name = "patients"
urlpatterns = [
    path("patients/", views.PatientTable.as_view(), name="patients"),
    path("patients/<uuid:pk>/", views.PatientRecord.as_view(), name="patient"),
    path("patients/list/", views.PatientListView.as_view(), name="patient-list"),
    path("patients/create/", views.PatientCreate.as_view(), name="patient-create"),
    path("patients/update/<uuid:pk>/", views.PatientUpdate.as_view(), name="patient-update"),
    path("patients/delete/<uuid:pk>/", views.PatientDelete.as_view(), name="patient-delete"),
]
