import pytest
from guardian.shortcuts import assign_perm, remove_perm

from tests.algorithms_tests.factories import AlgorithmFactory
from tests.archives_tests.factories import ArchiveFactory
from tests.factories import UserFactory
from tests.organizations_tests.factories import OrganizationFactory
from tests.reader_studies_tests.factories import ReaderStudyFactory
from tests.utils import get_view_for_user


@pytest.mark.django_db
class TestObjectPermissionRequiredViews:
    def test_open_views(self, client):
        o = OrganizationFactory()

        for viewname, kwargs in (("list", {}), ("detail", {"slug": o.slug})):
            response = get_view_for_user(
                client=client,
                viewname=f"organizations:{viewname}",
                reverse_kwargs=kwargs,
            )

            assert response.status_code == 200

    def test_permission_required_views(self, client):
        o = OrganizationFactory()
        u = UserFactory()

        for view_name, kwargs, permission, obj, redirect in [
            ("update", {"slug": o.slug}, "change_organization", o, None,),
            (
                "editors-update",
                {"slug": o.slug},
                "change_organization",
                o,
                None,
            ),
            (
                "members-update",
                {"slug": o.slug},
                "change_organization",
                o,
                None,
            ),
        ]:

            def _get_view():
                return get_view_for_user(
                    client=client,
                    viewname=f"organizations:{view_name}",
                    reverse_kwargs=kwargs,
                    user=u,
                )

            response = _get_view()
            if redirect is not None:
                assert response.status_code == 302
                assert response.url == redirect
            else:
                assert response.status_code == 403

            assign_perm(permission, u, obj)

            response = _get_view()
            assert response.status_code == 200

            remove_perm(permission, u, obj)


@pytest.mark.django_db
class TestOrganizationFilterViews:
    @pytest.mark.parametrize(
        # TODO: Challenge and External challenge tests
        "factory",
        (AlgorithmFactory, ArchiveFactory, ReaderStudyFactory),
    )
    def test_organization_filter_views(self, client, factory):
        org = OrganizationFactory()

        obj = factory(public=True)
        obj.organizations.set([OrganizationFactory()])

        def _get_org_detail():
            return get_view_for_user(
                client=client,
                viewname="organizations:detail",
                reverse_kwargs={"slug": org.slug},
            )

        response = _get_org_detail()
        assert response.status_code == 200
        assert {*response.context[-1]["object_list"]} == set()

        obj.organizations.add(org)

        response = _get_org_detail()
        assert response.status_code == 200
        assert {*response.context[-1]["object_list"]} == {obj}
