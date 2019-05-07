import datetime
import pytest
import pytz
import factory.fuzzy

from tests.factories import UserFactory
from tests.patients_tests.factories import PatientFactory
from tests.studies_tests.factories import StudyFactory
from tests.utils import get_view_for_user

from grandchallenge.subdomains.utils import reverse
from grandchallenge.studies.forms import StudyForm

"""" Tests the forms available for Study CRUD """


@pytest.mark.django_db
def test_study_display(client):
    study = StudyFactory()
    staff_user = UserFactory(is_staff=True)

    response = get_view_for_user(
        client=client, viewname="studies:list", user=staff_user
    )
    assert str(study.id) in response.rendered_content


@pytest.mark.django_db
def test_study_create(client):
    staff_user = UserFactory(is_staff=True)
    patient = PatientFactory()
    data = {
        "name": "test",
        "datetime": datetime.datetime(
            1950, 1, 1, 0, 0, 0, 0, pytz.UTC
        ).strftime("%d/%m/%Y %H:%M:%S"),
        "patient": patient.pk,
    }

    form = StudyForm(data=data)
    assert form.is_valid()

    form = StudyForm()
    assert not form.is_valid()

    response = get_view_for_user(
        viewname="studies:create",
        client=client,
        method=client.post,
        data=data,
        user=staff_user,
    )
    assert response.status_code == 302


@pytest.mark.django_db
def test_study_update(client):
    staff_user = UserFactory(is_staff=True)
    study = StudyFactory()
    data = {
        "name": "test",
        "datetime": datetime.datetime(
            1950, 1, 1, 0, 0, 0, 0, pytz.UTC
        ).strftime("%d/%m/%Y %H:%M:%S"),
        "patient": study.patient.pk,
    }

    form = StudyForm(data=data)
    assert form.is_valid()

    form = StudyForm()
    assert not form.is_valid()

    response = get_view_for_user(
        client=client,
        method=client.post,
        data=data,
        user=staff_user,
        url=reverse("studies:update", kwargs={"pk": study.pk}),
    )
    assert response.status_code == 302


@pytest.mark.django_db
def test_study_delete(client):
    study = StudyFactory()
    staff_user = UserFactory(is_staff=True)

    response = get_view_for_user(
        client=client,
        method=client.post,
        user=staff_user,
        url=reverse("studies:delete", kwargs={"pk": study.pk}),
    )

    assert response.status_code == 302
