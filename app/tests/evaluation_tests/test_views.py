from collections import namedtuple
from datetime import timedelta

import factory
import pytest
from django.db.models import signals
from django.utils import timezone
from guardian.shortcuts import assign_perm, remove_perm

from tests.evaluation_tests.factories import (
    EvaluationFactory,
    MethodFactory,
    PhaseFactory,
    SubmissionFactory,
)
from tests.factories import UserFactory
from tests.utils import get_view_for_user


@pytest.mark.django_db
class TestLoginViews:
    def test_login_redirect(self, client):
        e = EvaluationFactory()

        for view_name, kwargs in [
            ("phase-update", {"slug": e.submission.phase.slug}),
            ("method-create", {}),
            ("method-list", {}),
            ("method-detail", {"pk": e.method.pk}),
            ("submission-create", {"slug": e.submission.phase.slug}),
            ("submission-create-legacy", {"slug": e.submission.phase.slug}),
            ("submission-list", {}),
            ("submission-detail", {"pk": e.submission.pk}),
            ("list", {}),
            ("update", {"pk": e.pk}),
        ]:
            response = get_view_for_user(
                client=client,
                viewname=f"evaluation:{view_name}",
                reverse_kwargs={
                    "challenge_short_name": e.submission.phase.challenge.short_name,
                    **kwargs,
                },
                user=None,
            )

            assert response.status_code == 302
            assert response.url.startswith(
                f"https://testserver/users/signin/?next=http%3A//"
                f"{e.submission.phase.challenge.short_name}.testserver/"
            )

    def test_open_views(self, client):
        e = EvaluationFactory(submission__phase__challenge__hidden=False)

        for view_name, kwargs in [
            ("leaderboard", {"slug": e.submission.phase.slug}),
            ("detail", {"pk": e.pk}),
        ]:
            response = get_view_for_user(
                client=client,
                viewname=f"evaluation:{view_name}",
                reverse_kwargs={
                    "challenge_short_name": e.submission.phase.challenge.short_name,
                    **kwargs,
                },
                user=None,
            )

            assert response.status_code == 200


@pytest.mark.django_db
class TestObjectPermissionRequiredViews:
    def test_permission_required_views(self, client):
        e = EvaluationFactory()
        u = UserFactory()

        for view_name, kwargs, permission, obj in [
            (
                "phase-update",
                {"slug": e.submission.phase.slug},
                "change_phase",
                e.submission.phase,
            ),
            (
                "method-create",
                {},
                "change_challenge",
                e.submission.phase.challenge,
            ),
            ("method-detail", {"pk": e.method.pk}, "view_method", e.method),
            (
                "submission-create",
                {"slug": e.submission.phase.slug},
                "create_phase_submission",
                e.submission.phase,
            ),
            (
                "submission-create-legacy",
                {"slug": e.submission.phase.slug},
                "change_challenge",
                e.submission.phase.challenge,
            ),
            (
                "submission-detail",
                {"pk": e.submission.pk},
                "view_submission",
                e.submission,
            ),
            ("update", {"pk": e.pk}, "change_evaluation", e),
            ("detail", {"pk": e.pk}, "view_evaluation", e),
        ]:
            response = get_view_for_user(
                client=client,
                viewname=f"evaluation:{view_name}",
                reverse_kwargs={
                    "challenge_short_name": e.submission.phase.challenge.short_name,
                    **kwargs,
                },
                user=u,
            )

            assert response.status_code == 403

            assign_perm(permission, u, obj)

            response = get_view_for_user(
                client=client,
                viewname=f"evaluation:{view_name}",
                reverse_kwargs={
                    "challenge_short_name": e.submission.phase.challenge.short_name,
                    **kwargs,
                },
                user=u,
            )

            assert response.status_code == 200

            remove_perm(permission, u, obj)

    def test_permission_filtered_views(self, client):
        u = UserFactory()

        p = PhaseFactory()
        m = MethodFactory(phase=p)
        s = SubmissionFactory(phase=p, creator=u)
        e = EvaluationFactory(method=m, submission=s)

        for view_name, kwargs, permission, obj in [
            ("method-list", {}, "view_method", m),
            ("submission-list", {}, "view_submission", s),
            ("list", {}, "view_evaluation", e),
            (
                "leaderboard",
                {"slug": e.submission.phase.slug},
                "view_evaluation",
                e,
            ),
        ]:
            assign_perm(permission, u, obj)

            response = get_view_for_user(
                client=client,
                viewname=f"evaluation:{view_name}",
                reverse_kwargs={
                    "challenge_short_name": e.submission.phase.challenge.short_name,
                    **kwargs,
                },
                user=u,
            )

            assert response.status_code == 200
            assert obj in response.context[-1]["object_list"]

            remove_perm(permission, u, obj)

            response = get_view_for_user(
                client=client,
                viewname=f"evaluation:{view_name}",
                reverse_kwargs={
                    "challenge_short_name": e.submission.phase.challenge.short_name,
                    **kwargs,
                },
                user=u,
            )

            assert response.status_code == 200
            assert obj not in response.context[-1]["object_list"]


def submission_and_evaluation(*, phase, creator):
    """Creates a submission and an evaluation for that submission."""
    s = SubmissionFactory(phase=phase, creator=creator)
    e = EvaluationFactory(submission=s)
    return s, e


def submissions_and_evaluations(two_challenge_sets):
    """
    Create (e)valuations and (s)ubmissions for each (p)articipant and
    (c)hallenge.
    """
    SubmissionsAndEvaluations = namedtuple(
        "SubmissionsAndEvaluations",
        [
            "p_s1",
            "p_s2",
            "p1_s1",
            "p12_s1_c1",
            "p12_s1_c2",
            "e_p_s1",
            "e_p_s2",
            "e_p1_s1",
            "e_p12_s1_c1",
            "e_p12_s1_c2",
        ],
    )
    # participant 0, submission 1, challenge 1, etc
    p_s1, e_p_s1 = submission_and_evaluation(
        phase=two_challenge_sets.challenge_set_1.challenge.phase_set.get(),
        creator=two_challenge_sets.challenge_set_1.participant,
    )
    p_s2, e_p_s2 = submission_and_evaluation(
        phase=two_challenge_sets.challenge_set_1.challenge.phase_set.get(),
        creator=two_challenge_sets.challenge_set_1.participant,
    )
    p1_s1, e_p1_s1 = submission_and_evaluation(
        phase=two_challenge_sets.challenge_set_1.challenge.phase_set.get(),
        creator=two_challenge_sets.challenge_set_1.participant1,
    )
    # participant12, submission 1 to each challenge
    p12_s1_c1, e_p12_s1_c1 = submission_and_evaluation(
        phase=two_challenge_sets.challenge_set_1.challenge.phase_set.get(),
        creator=two_challenge_sets.participant12,
    )
    p12_s1_c2, e_p12_s1_c2 = submission_and_evaluation(
        phase=two_challenge_sets.challenge_set_2.challenge.phase_set.get(),
        creator=two_challenge_sets.participant12,
    )
    return SubmissionsAndEvaluations(
        p_s1,
        p_s2,
        p1_s1,
        p12_s1_c1,
        p12_s1_c2,
        e_p_s1,
        e_p_s2,
        e_p1_s1,
        e_p12_s1_c1,
        e_p12_s1_c2,
    )


@pytest.mark.django_db
@factory.django.mute_signals(signals.post_save)
def test_submission_list(client, two_challenge_sets):
    p_s1, p_s2, p1_s1, p12_s1_c1, p12_s1_c2, *_ = submissions_and_evaluations(
        two_challenge_sets
    )
    # Only submissions relevant to this challenge should be listed
    response = get_view_for_user(
        viewname="evaluation:submission-list",
        challenge=two_challenge_sets.challenge_set_1.challenge,
        client=client,
        user=two_challenge_sets.participant12,
    )
    assert str(p12_s1_c1.pk) in response.rendered_content
    assert str(p12_s1_c2.pk) not in response.rendered_content
    assert str(p_s1.pk) not in response.rendered_content
    assert str(p_s2.pk) not in response.rendered_content
    assert str(p1_s1.pk) not in response.rendered_content


@pytest.mark.django_db
def test_submission_time_limit(client, two_challenge_sets):
    phase = two_challenge_sets.challenge_set_1.challenge.phase_set.get()

    SubmissionFactory(
        phase=phase, creator=two_challenge_sets.challenge_set_1.participant,
    )

    def get_submission_view():
        return get_view_for_user(
            viewname="evaluation:submission-create",
            client=client,
            user=two_challenge_sets.challenge_set_1.participant,
            reverse_kwargs={
                "challenge_short_name": two_challenge_sets.challenge_set_1.challenge.short_name,
                "slug": two_challenge_sets.challenge_set_1.challenge.phase_set.get().slug,
            },
        )

    assert "make 9 more" in get_submission_view().rendered_content

    s = SubmissionFactory(
        phase=phase, creator=two_challenge_sets.challenge_set_1.participant,
    )
    s.created = timezone.now() - timedelta(hours=23)
    s.save()
    assert "make 8 more" in get_submission_view().rendered_content

    s = SubmissionFactory(
        phase=phase, creator=two_challenge_sets.challenge_set_1.participant,
    )
    s.created = timezone.now() - timedelta(hours=25)
    s.save()
    assert "make 8 more" in get_submission_view().rendered_content


@pytest.mark.django_db
@factory.django.mute_signals(signals.post_save)
def test_evaluation_list(client, two_challenge_sets):
    (
        *_,
        e_p_s1,
        e_p_s2,
        e_p1_s1,
        e_p12_s1_c1,
        e_p12_s1_c2,
    ) = submissions_and_evaluations(two_challenge_sets)
    # Participants should only be able to see their own evaluations
    response = get_view_for_user(
        viewname="evaluation:list",
        challenge=two_challenge_sets.challenge_set_1.challenge,
        client=client,
        user=two_challenge_sets.challenge_set_1.participant,
    )
    assert str(e_p_s1.pk) in response.rendered_content
    assert str(e_p_s2.pk) in response.rendered_content
    assert str(e_p1_s1.pk) not in response.rendered_content
    assert str(e_p12_s1_c1.pk) not in response.rendered_content
    assert str(e_p12_s1_c2.pk) not in response.rendered_content
    # Admins should be able to see all evaluations
    response = get_view_for_user(
        viewname="evaluation:list",
        challenge=two_challenge_sets.challenge_set_1.challenge,
        client=client,
        user=two_challenge_sets.challenge_set_1.admin,
    )
    assert str(e_p_s1.pk) in response.rendered_content
    assert str(e_p_s2.pk) in response.rendered_content
    assert str(e_p1_s1.pk) in response.rendered_content
    assert str(e_p12_s1_c1.pk) in response.rendered_content
    assert str(e_p12_s1_c2.pk) not in response.rendered_content
    # Only evaluations relevant to this challenge should be listed
    response = get_view_for_user(
        viewname="evaluation:list",
        challenge=two_challenge_sets.challenge_set_1.challenge,
        client=client,
        user=two_challenge_sets.participant12,
    )
    assert str(e_p12_s1_c1.pk) in response.rendered_content
    assert str(e_p12_s1_c2.pk) not in response.rendered_content
    assert str(e_p_s1.pk) not in response.rendered_content
    assert str(e_p_s2.pk) not in response.rendered_content
    assert str(e_p1_s1.pk) not in response.rendered_content
