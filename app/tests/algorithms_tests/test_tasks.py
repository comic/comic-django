import pytest

from grandchallenge.algorithms.models import Job
from grandchallenge.algorithms.tasks import create_algorithm_jobs
from tests.algorithms_tests.factories import AlgorithmImageFactory
from tests.cases_tests.factories import RawImageUploadSessionFactory
from tests.factories import ImageFactory, UserFactory


@pytest.mark.django_db
def test_create_jobs_is_idempotent():
    image = ImageFactory()

    ai = AlgorithmImageFactory()
    user = UserFactory()
    image.origin.algorithm_image = ai
    image.origin.creator = user
    image.origin.save()

    assert Job.objects.count() == 0

    create_algorithm_jobs(upload_session_pk=image.origin.pk)

    assert Job.objects.count() == 1

    j = Job.objects.all()[0]
    assert j.algorithm_image == ai
    assert j.creator == user
    assert j.inputs.get(interface__slug="generic-medical-image").image == image

    # Running the job twice should not result in new jobs
    create_algorithm_jobs(upload_session_pk=image.origin.pk)

    assert Job.objects.count() == 1

    # Changing the algorithm image should create a new job
    image.origin.algorithm_image = AlgorithmImageFactory()
    image.origin.save()

    create_algorithm_jobs(upload_session_pk=image.origin.pk)

    assert Job.objects.count() == 2


@pytest.mark.django_db
def test_create_jobs_is_limited():
    user = UserFactory()
    riu = RawImageUploadSessionFactory()
    riu.algorithm_image.algorithm.job_credit = 400
    riu.algorithm_image.algorithm.save()
    riu.creator = user

    for _ in range(3):
        ImageFactory(origin=riu),
    riu.save()

    assert Job.objects.count() == 0

    create_algorithm_jobs(upload_session_pk=riu.pk)

    # A maximum of 2 jobs should be created (standard nr of credits is 1000 per month)
    assert Job.objects.count() == 2
