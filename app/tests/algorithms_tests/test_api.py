import pytest

from grandchallenge.algorithms.models import Job

from tests.utils import get_view_for_user
from tests.factories import UserFactory
from tests.algorithms_tests.factories import (
    AlgorithmFactory,
    JobFactory,
    ResultFactory,
    ImageFactory,
)


@pytest.mark.django_db
def test_algorithm_list(client):
    user = UserFactory(is_staff=True)
    algo1, algo2 = AlgorithmFactory(), AlgorithmFactory()
    job1, job2 = (JobFactory(algorithm=algo1), JobFactory(algorithm=algo2))
    result1, result2 = (
        ResultFactory(job=job1, output={"cancer_score": 0.01}),
        ResultFactory(job=job2, output={"cancer_score": 0.5}),
    )
    response = get_view_for_user(
        viewname="api:algorithm-list", user=user, client=client
    )
    assert response.status_code == 200
    assert response.json()["count"] == 2

    response = get_view_for_user(
        viewname="api:algorithm-detail",
        reverse_kwargs={"pk": algo1.pk},
        user=user,
        client=client,
    )
    assert response.status_code == 200

    response = get_view_for_user(
        viewname="api:algorithms-job-list", user=user, client=client
    )
    assert response.status_code == 200
    assert response.json()["results"][0]["pk"] == str(job1.pk)
    assert response.json()["results"][0][
        "algorithm"
    ] == "http://testserver/api/v1/algorithms/{}/".format(algo1.pk)
    assert response.json()["results"][1]["pk"] == str(job2.pk)
    assert response.json()["results"][1][
        "algorithm"
    ] == "http://testserver/api/v1/algorithms/{}/".format(algo2.pk)

    response = get_view_for_user(
        viewname="api:algorithms-result-list", user=user, client=client
    )
    assert response.status_code == 200
    assert response.json()["results"][0]["pk"] == str(result1.pk)
    assert response.json()["results"][0][
        "job"
    ] == "http://testserver/api/v1/algorithms/jobs/{}/".format(job1.pk)
    assert response.json()["results"][0]["output"] == {"cancer_score": 0.01}
    assert response.json()["results"][1]["pk"] == str(result2.pk)
    assert response.json()["results"][1][
        "job"
    ] == "http://testserver/api/v1/algorithms/jobs/{}/".format(job2.pk)
    assert response.json()["results"][1]["output"] == {"cancer_score": 0.5}


@pytest.mark.django_db
def test_algorithm_api_permissions(client):
    tests = [(UserFactory(), 403), (UserFactory(is_staff=True), 200)]
    algorithm = AlgorithmFactory()

    for test in tests:
        response = get_view_for_user(
            client=client,
            viewname="api:algorithm-list",
            user=test[0],
            content_type="application/json",
        )
        assert response.status_code == test[1]

        response = get_view_for_user(
            client=client,
            viewname="api:algorithm-detail",
            reverse_kwargs={"pk": algorithm.pk},
            user=test[0],
            content_type="application/json",
        )
        assert response.status_code == test[1]


@pytest.mark.django_db
def test_job_api_permissions(client):
    tests = [(UserFactory(), 403), (UserFactory(is_staff=True), 200)]
    job = JobFactory()

    for test in tests:
        response = get_view_for_user(
            client=client,
            viewname="api:algorithms-job-list",
            user=test[0],
            content_type="application/json",
        )
        assert response.status_code == test[1]

        response = get_view_for_user(
            client=client,
            viewname="api:algorithms-job-detail",
            reverse_kwargs={"pk": job.pk},
            user=test[0],
            content_type="application/json",
        )
        assert response.status_code == test[1]


@pytest.mark.django_db
def test_result_api_permissions(client):
    tests = [(UserFactory(), 403), (UserFactory(is_staff=True), 200)]
    result = ResultFactory()

    for test in tests:
        response = get_view_for_user(
            client=client,
            viewname="api:algorithms-result-list",
            user=test[0],
            content_type="application/json",
        )
        assert response.status_code == test[1]

        response = get_view_for_user(
            client=client,
            viewname="api:algorithms-result-detail",
            reverse_kwargs={"pk": result.pk},
            user=test[0],
            content_type="application/json",
        )
        assert response.status_code == test[1]


@pytest.mark.django_db
def test_job_create(client):
    im = ImageFactory()

    algo = AlgorithmFactory()

    user = UserFactory(is_staff=True)

    response = get_view_for_user(
        viewname="api:algorithms-job-list",
        user=user,
        client=client,
        method=client.post,
        data={"image": im.api_url, "algorithm": algo.api_url},
        content_type="application/json",
    )
    assert response.status_code == 201

    job = Job.objects.get(pk=response.data.get("pk"))

    assert job.image == im
    assert job.algorithm == algo


@pytest.mark.django_db
@pytest.mark.parametrize(
    "is_staff, expected_response", [(False, 403), (True, 201)]
)
def test_job_post_permissions(client, is_staff, expected_response):
    # Staff users should be able to post a job
    user = UserFactory(is_staff=is_staff)
    im = ImageFactory()
    algo = AlgorithmFactory()

    response = get_view_for_user(
        viewname="api:algorithms-job-list",
        user=user,
        client=client,
        method=client.post,
        data={"image": im.api_url, "algorithm": algo.api_url},
        content_type="application/json",
    )
    assert response.status_code == expected_response
