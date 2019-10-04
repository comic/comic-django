import pytest
from django.contrib.auth.models import Group
from guardian.shortcuts import get_group_perms

from tests.algorithms_tests.factories import (
    AlgorithmFactory,
    AlgorithmImageFactory,
)
from tests.algorithms_tests.utils import TwoAlgorithms
from tests.factories import UserFactory
from tests.utils import get_view_for_user


@pytest.mark.django_db
def test_algorithm_creators_group_has_perm(settings):
    creators_group = Group.objects.get(
        name=settings.ALGORITHMS_CREATORS_GROUP_NAME
    )
    assert creators_group.permissions.filter(codename="add_algorithm").exists()


@pytest.mark.django_db
def test_algorithm_groups_permissions_are_assigned():
    alg = AlgorithmFactory()

    editors_perms = get_group_perms(alg.editors_group, alg)
    assert "view_algorithm" in editors_perms
    assert "change_algorithm" in editors_perms

    users_perms = get_group_perms(alg.users_group, alg)
    assert "view_algorithm" in users_perms
    assert "change_algorithm" not in users_perms


@pytest.mark.django_db
def test_algorithm_image_group_permissions_are_assigned():
    ai = AlgorithmImageFactory()

    perms = get_group_perms(ai.algorithm.editors_group, ai)
    assert "view_algorithmimage" in perms
    assert "change_algorithmimage" in perms


@pytest.mark.django_db
def test_algorithm_create_page(client, settings):
    response = get_view_for_user(viewname="algorithms:create", client=client)
    assert response.status_code == 302
    assert response.url.startswith(settings.LOGIN_URL)

    user = UserFactory()

    response = get_view_for_user(
        viewname="algorithms:create", client=client, user=user
    )
    assert response.status_code == 403

    Group.objects.get(
        name=settings.ALGORITHMS_CREATORS_GROUP_NAME
    ).user_set.add(user)

    response = get_view_for_user(
        viewname="algorithms:create", client=client, user=user
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_algorithm_detail_view_permissions(client):
    alg_set = TwoAlgorithms()

    tests = (
        (None, alg_set.alg1, 302),
        (None, alg_set.alg2, 302),
        (alg_set.creator, alg_set.alg1, 403),
        (alg_set.creator, alg_set.alg2, 403),
        (alg_set.editor1, alg_set.alg1, 200),
        (alg_set.editor1, alg_set.alg2, 403),
        (alg_set.user1, alg_set.alg1, 200),
        (alg_set.user1, alg_set.alg2, 403),
        (alg_set.editor2, alg_set.alg1, 403),
        (alg_set.editor2, alg_set.alg2, 200),
        (alg_set.user2, alg_set.alg1, 403),
        (alg_set.user2, alg_set.alg2, 200),
        (alg_set.u, alg_set.alg1, 403),
        (alg_set.u, alg_set.alg2, 403),
    )

    for test in tests:
        response = get_view_for_user(
            url=test[1].get_absolute_url(), client=client, user=test[0]
        )
        assert response.status_code == test[2]


@pytest.mark.django_db
@pytest.mark.parametrize("view_name", ["update", "image-create"])
def test_algorithm_edit_view_permissions(client, view_name):
    alg_set = TwoAlgorithms()

    tests = (
        (None, alg_set.alg1, 302),
        (None, alg_set.alg2, 302),
        (alg_set.creator, alg_set.alg1, 403),
        (alg_set.creator, alg_set.alg2, 403),
        (alg_set.editor1, alg_set.alg1, 200),
        (alg_set.editor1, alg_set.alg2, 403),
        (alg_set.user1, alg_set.alg1, 403),
        (alg_set.user1, alg_set.alg2, 403),
        (alg_set.editor2, alg_set.alg1, 403),
        (alg_set.editor2, alg_set.alg2, 200),
        (alg_set.user2, alg_set.alg1, 403),
        (alg_set.user2, alg_set.alg2, 403),
        (alg_set.u, alg_set.alg1, 403),
        (alg_set.u, alg_set.alg2, 403),
    )

    for test in tests:
        response = get_view_for_user(
            viewname=f"algorithms:{view_name}",
            client=client,
            user=test[0],
            reverse_kwargs={"slug": test[1].slug},
        )
        assert response.status_code == test[2]


@pytest.mark.django_db
@pytest.mark.parametrize("view_name", ["image-detail", "image-update"])
def test_algorithm_edit_view_permissions(client, view_name):
    alg_set = TwoAlgorithms()

    im1, im2 = (
        AlgorithmImageFactory(algorithm=alg_set.alg1),
        AlgorithmImageFactory(algorithm=alg_set.alg2),
    )

    tests = (
        (None, im1, 302),
        (None, im2, 302),
        (alg_set.creator, im1, 403),
        (alg_set.creator, im2, 403),
        (alg_set.editor1, im1, 200),
        (alg_set.editor1, im2, 403),
        (alg_set.user1, im1, 403),
        (alg_set.user1, im2, 403),
        (alg_set.editor2, im1, 403),
        (alg_set.editor2, im2, 200),
        (alg_set.user2, im1, 403),
        (alg_set.user2, im2, 403),
        (alg_set.u, im1, 403),
        (alg_set.u, im2, 403),
    )

    for test in tests:
        response = get_view_for_user(
            viewname=f"algorithms:{view_name}",
            client=client,
            user=test[0],
            reverse_kwargs={"slug": test[1].algorithm.slug, "pk": test[1].pk},
        )
        assert response.status_code == test[2]
