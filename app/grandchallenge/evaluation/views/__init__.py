from datetime import datetime, timedelta
from typing import Dict

from dateutil.relativedelta import relativedelta
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.db.models import Q
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
)
from guardian.mixins import (
    LoginRequiredMixin,
    PermissionListMixin,
    PermissionRequiredMixin as ObjectPermissionRequiredMixin,
)
from ipware import get_client_ip

from grandchallenge.core.views import Column, PaginatedTableListView
from grandchallenge.evaluation.forms import (
    LegacySubmissionForm,
    MethodForm,
    PhaseForm,
    SubmissionForm,
)
from grandchallenge.evaluation.models import (
    Evaluation,
    Method,
    Phase,
    Submission,
)
from grandchallenge.jqfileupload.widgets.uploader import StagedAjaxFile
from grandchallenge.subdomains.utils import reverse, reverse_lazy
from grandchallenge.teams.models import Team


class PhaseUpdate(
    LoginRequiredMixin,
    ObjectPermissionRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    form_class = PhaseForm
    success_message = "Configuration successfully updated"
    permission_required = "change_phase"
    raise_exception = True
    login_url = reverse_lazy("userena_signin")

    def get_object(self, queryset=None):
        return Phase.objects.get(
            challenge=self.request.challenge, slug=self.kwargs["slug"]
        )

    def get_success_url(self):
        return reverse(
            "evaluation:leaderboard",
            kwargs={
                "challenge_short_name": self.request.challenge.short_name,
                "slug": self.kwargs["slug"],
            },
        )


class MethodCreate(
    LoginRequiredMixin, ObjectPermissionRequiredMixin, CreateView
):
    model = Method
    form_class = MethodForm
    permission_required = "change_challenge"
    raise_exception = True
    login_url = reverse_lazy("userena_signin")

    def get_permission_object(self):
        return self.request.challenge

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {"user": self.request.user, "challenge": self.request.challenge}
        )
        return kwargs

    def form_valid(self, form):
        form.instance.creator = self.request.user

        uploaded_file: StagedAjaxFile = form.cleaned_data["chunked_upload"][0]
        form.instance.staged_image_uuid = uploaded_file.uuid

        return super().form_valid(form)


class MethodList(LoginRequiredMixin, PermissionListMixin, ListView):
    model = Method
    permission_required = "view_method"
    login_url = reverse_lazy("userena_signin")

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(phase__challenge=self.request.challenge)


class MethodDetail(
    LoginRequiredMixin, ObjectPermissionRequiredMixin, DetailView
):
    model = Method
    permission_required = "view_method"
    raise_exception = True
    login_url = reverse_lazy("userena_signin")


class SubmissionCreateBase(SuccessMessageMixin, CreateView):
    """
    Base class for the submission creation forms.

    It has no permissions, do not use it directly! See the subclasses.
    """

    model = Submission
    success_message = (
        "Your submission was successful. "
        "Your result will appear on the leaderboard when it is ready."
    )

    @cached_property
    def phase(self):
        return Phase.objects.get(
            challenge=self.request.challenge, slug=self.kwargs["slug"]
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs.update(
            {
                "user": self.request.user,
                "display_comment_field": self.phase.allow_submission_comments,
                "supplementary_file_choice": self.phase.supplementary_file_choice,
                "supplementary_file_label": self.phase.supplementary_file_label,
                "supplementary_file_help_text": self.phase.supplementary_file_help_text,
                "publication_url_choice": self.phase.publication_url_choice,
                "algorithm_submission": self.phase.submission_kind
                == self.phase.SubmissionKind.ALGORITHM,
            }
        )

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            self.get_next_submission(
                max_subs=self.phase.daily_submission_limit
            )
        )

        pending_evaluations = Evaluation.objects.filter(
            submission__phase__challenge=self.request.challenge,
            submission__creator=self.request.user,
            status__in=(Evaluation.PENDING, Evaluation.STARTED),
        ).count()

        context.update(
            {"pending_evaluations": pending_evaluations, "phase": self.phase}
        )

        return context

    def get_next_submission(
        self, *, max_subs: int, period: timedelta = None, now: datetime = None
    ) -> Dict:
        """
        Determines the number of submissions left for the user in a given time
        period, and when they can next submit.

        :return: A dictionary containing remaining_submissions (int) and
        next_submission_at (datetime)
        """
        if now is None:
            now = timezone.now()

        if period is None:
            period = timedelta(days=1)

        subs = (
            Submission.objects.filter(
                phase__challenge=self.request.challenge,
                creator=self.request.user,
                created__gte=now - period,
            )
            .exclude(evaluation__status=Evaluation.FAILURE)
            .order_by("-created")
            .distinct()
        )

        try:
            next_sub_at = subs[max_subs - 1].created + period
        except (IndexError, AssertionError):
            next_sub_at = now

        return {
            "remaining_submissions": max_subs - len(subs),
            "next_submission_at": next_sub_at,
        }

    def form_valid(self, form):
        if form.instance.creator is None:
            form.instance.creator = self.request.user

        client_ip, _ = get_client_ip(self.request)
        form.instance.creators_ip = client_ip
        form.instance.creators_user_agent = self.request.META.get(
            "HTTP_USER_AGENT", ""
        )

        form.instance.phase = self.phase

        if "algorithm" in form.cleaned_data:
            # Algorithm submission
            form.instance.algorithm_image = form.cleaned_data[
                "algorithm"
            ].latest_ready_image
        else:
            # Predictions file submission
            uploaded_file = form.cleaned_data["chunked_upload"][0]
            with uploaded_file.open() as f:
                form.instance.predictions_file.save(
                    uploaded_file.name, File(f)
                )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "evaluation:submission-list",
            kwargs={
                "challenge_short_name": self.object.phase.challenge.short_name
            },
        )


class SubmissionCreate(
    LoginRequiredMixin, ObjectPermissionRequiredMixin, SubmissionCreateBase
):
    form_class = SubmissionForm
    permission_required = "create_phase_submission"
    raise_exception = True
    login_url = reverse_lazy("userena_signin")

    def get_permission_object(self):
        return self.phase


class LegacySubmissionCreate(
    LoginRequiredMixin, ObjectPermissionRequiredMixin, SubmissionCreateBase
):
    form_class = LegacySubmissionForm
    permission_required = "change_challenge"
    raise_exception = True
    login_url = reverse_lazy("userena_signin")

    def get_permission_object(self):
        return self.request.challenge

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"challenge": self.request.challenge})
        return kwargs


class SubmissionList(LoginRequiredMixin, PermissionListMixin, ListView):
    model = Submission
    permission_required = "view_submission"
    login_url = reverse_lazy("userena_signin")

    def get_queryset(self):
        queryset = super().get_queryset()
        return (
            queryset.filter(phase__challenge=self.request.challenge)
            .select_related(
                "creator__user_profile",
                "creator__verification",
                "phase__challenge",
            )
            .prefetch_related("evaluation_set")
        )


class SubmissionDetail(
    LoginRequiredMixin, ObjectPermissionRequiredMixin, DetailView
):
    model = Submission
    permission_required = "view_submission"
    raise_exception = True
    login_url = reverse_lazy("userena_signin")


class TeamContextMixin:
    @cached_property
    def user_teams(self):
        if self.request.challenge.use_teams:
            user_teams = {
                teammember.user.username: (team.name, team.get_absolute_url())
                for team in Team.objects.filter(
                    challenge=self.request.challenge
                )
                .select_related("challenge")
                .prefetch_related("teammember_set__user")
                for teammember in team.teammember_set.all()
            }
        else:
            user_teams = {}

        return user_teams

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({"user_teams": self.user_teams})
        return context


class EvaluationList(
    LoginRequiredMixin, PermissionListMixin, TeamContextMixin, ListView
):
    model = Evaluation
    permission_required = "view_evaluation"
    login_url = reverse_lazy("userena_signin")

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            submission__phase__challenge=self.request.challenge
        ).select_related(
            "submission__creator__user_profile",
            "submission__creator__verification",
            "submission__phase__challenge",
        )

        if self.request.challenge.is_admin(self.request.user):
            return queryset
        else:
            return queryset.filter(
                Q(submission__creator__pk=self.request.user.pk)
            )


class EvaluationDetail(ObjectPermissionRequiredMixin, DetailView):
    model = Evaluation
    permission_required = "view_evaluation"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            metrics = self.object.outputs.get(
                interface__slug="metrics-json-file"
            ).value
        except ObjectDoesNotExist:
            metrics = None

        context.update({"metrics": metrics})

        return context


class LeaderboardRedirect(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        # Redirect old leaderboard urls to the first leaderboard for this
        # challenge
        return reverse(
            "evaluation:leaderboard",
            kwargs={
                "challenge_short_name": self.request.challenge.short_name,
                "slug": self.request.challenge.phase_set.first().slug,
            },
        )


class LeaderboardDetail(
    PermissionListMixin, TeamContextMixin, PaginatedTableListView
):
    model = Evaluation
    template_name = "evaluation/leaderboard_detail.html"
    row_template = "evaluation/leaderboard_row.html"
    search_fields = ["pk", "submission__creator__username"]
    permission_required = "view_evaluation"

    @cached_property
    def phase(self):
        return Phase.objects.get(
            challenge=self.request.challenge, slug=self.kwargs["slug"]
        )

    @property
    def columns(self):
        columns = [
            Column(
                title="Current #"
                if "leaderboardDate" in self.request.GET
                else "#",
                sort_field="rank",
            ),
            Column(
                title="User (Team)"
                if self.request.challenge.use_teams
                else "User",
                sort_field="submission__creator__username",
            ),
            Column(title="Created", sort_field="created"),
        ]

        if self.phase.scoring_method_choice == self.phase.MEAN:
            columns.append(Column(title="Mean Position", sort_field="rank"))
        elif self.phase.scoring_method_choice == self.phase.MEDIAN:
            columns.append(Column(title="Median Position", sort_field="rank"))

        if self.phase.scoring_method_choice == self.phase.ABSOLUTE:
            columns.append(
                Column(title=self.phase.score_title, sort_field="rank")
            )
        else:
            columns.append(
                Column(
                    title=f"{self.phase.score_title} (Position)",
                    sort_field="rank",
                    toggleable=True,
                )
            )

        for c in self.phase.extra_results_columns:
            columns.append(
                Column(
                    title=c["title"]
                    if self.phase.scoring_method_choice == self.phase.ABSOLUTE
                    else f"{c['title']} (Position)",
                    sort_field="rank",
                    toggleable=True,
                )
            )

        if self.phase.display_submission_comments:
            columns.append(
                Column(title="Comment", sort_field="submission__comment")
            )

        if self.phase.show_publication_url:
            columns.append(
                Column(
                    title="Publication",
                    sort_field="submission__publication_url",
                )
            )

        if self.phase.show_supplementary_file_link:
            columns.append(
                Column(
                    title=self.phase.supplementary_file_label,
                    sort_field="submission__supplementary_file",
                )
            )

        return columns

    def get_row_context(self, job, *args, **kwargs):
        return {
            "object": job,
            "user_teams": self.user_teams,
        }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        limit = 1000
        context.update(
            {
                "phase": self.phase,
                "now": now().isoformat(),
                "limit": limit,
                "offsets": range(0, context["object_list"].count(), limit),
            }
        )
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = self.filter_by_date(queryset=queryset)
        queryset = (
            queryset.select_related(
                "submission__creator__user_profile",
                "submission__creator__verification",
                "submission__phase__challenge",
            )
            .filter(
                submission__phase=self.phase,
                published=True,
                status=Evaluation.SUCCESS,
                rank__gt=0,
            )
            .annotate(
                metrics=ArrayAgg(
                    "outputs__value",
                    filter=Q(outputs__interface__slug="metrics-json-file"),
                )
            )
        )
        return queryset

    def filter_by_date(self, queryset):
        if "leaderboardDate" in self.request.GET:
            year, month, day = self.request.GET["leaderboardDate"].split("-")
            before = datetime(
                year=int(year), month=int(month), day=int(day)
            ) + relativedelta(days=1)
            return queryset.filter(submission__created__lt=before)
        else:
            return queryset


class EvaluationUpdate(
    LoginRequiredMixin,
    ObjectPermissionRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = Evaluation
    fields = ("published",)
    success_message = "Result successfully updated."
    permission_required = "change_evaluation"
    raise_exception = True
    login_url = reverse_lazy("userena_signin")
