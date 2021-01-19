import pytest

from tests.algorithms_tests.factories import AlgorithmFactory
from tests.archives_tests.factories import ArchiveFactory
from tests.factories import UserFactory, WorkstationFactory
from tests.organizations_tests.factories import OrganizationFactory
from tests.reader_studies_tests.factories import ReaderStudyFactory
from tests.utils import get_view_for_user


@pytest.mark.django_db
class TestGroupManagementViews:
    @pytest.mark.parametrize(
        "factory,namespace,view_name,group_attr",
        (
            (OrganizationFactory, "organizations", "members", "members_group"),
            (OrganizationFactory, "organizations", "editors", "editors_group"),
            (AlgorithmFactory, "algorithms", "users", "users_group"),
            (AlgorithmFactory, "algorithms", "editors", "editors_group"),
            (ArchiveFactory, "archives", "users", "users_group"),
            (ArchiveFactory, "archives", "uploaders", "uploaders_group"),
            (ArchiveFactory, "archives", "editors", "editors_group"),
            (ReaderStudyFactory, "reader-studies", "readers", "readers_group"),
            (ReaderStudyFactory, "reader-studies", "editors", "editors_group"),
            (WorkstationFactory, "workstations", "users", "users_group"),
            (WorkstationFactory, "workstations", "editors", "editors_group"),
        ),
    )
    def test_group_management(
        self, client, factory, namespace, view_name, group_attr
    ):
        o = factory()
        group = getattr(o, group_attr)

        admin = UserFactory()
        u = UserFactory()

        assert not group.user_set.filter(pk=u.pk).exists()

        def get_user_autocomplete():
            return get_view_for_user(
                client=client,
                viewname="users-autocomplete",
                user=admin,
                data={"q": u.username.lower()},
            )

        response = get_user_autocomplete()
        assert response.status_code == 403

        o.add_editor(admin)

        response = get_user_autocomplete()
        assert response.status_code == 200
        assert response.json()["results"] == [
            {
                "id": str(u.pk),
                "text": str(u.username),
                "selected_text": str(u.username),
            }
        ]

        response = get_view_for_user(
            client=client,
            viewname=f"{namespace}:{view_name}-update",
            reverse_kwargs={"slug": o.slug},
            user=admin,
            method=client.post,
            data={"action": "ADD", "user": u.pk},
        )
        assert response.status_code == 302
        assert group.user_set.filter(pk=u.pk).exists()

        response = get_view_for_user(
            client=client,
            viewname=f"{namespace}:{view_name}-update",
            reverse_kwargs={"slug": o.slug},
            user=admin,
            method=client.post,
            data={"action": "REMOVE", "user": u.pk},
        )
        assert response.status_code == 302
        assert not group.user_set.filter(pk=u.pk).exists()
