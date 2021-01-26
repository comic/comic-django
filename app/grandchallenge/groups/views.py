from dal import autocomplete
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import CharField, Q, Value
from django.db.models.functions import Concat
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.views.generic import FormView
from guardian.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin as ObjectPermissionRequiredMixin,
)
from guardian.shortcuts import get_objects_for_user

from grandchallenge.verifications.models import Verification


class UserGroupUpdateMixin(
    LoginRequiredMixin,
    ObjectPermissionRequiredMixin,
    SuccessMessageMixin,
    FormView,
):
    raise_exception = True

    def get_permission_object(self):
        return self.obj

    @property
    def obj(self):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"object": self.obj, "role": self.get_form().role})
        return context

    def get_success_url(self):
        return self.obj.get_absolute_url()

    def form_valid(self, form):
        form.add_or_remove_user(obj=self.obj)
        return super().form_valid(form)


class UserAutocomplete(
    LoginRequiredMixin, UserPassesTestMixin, autocomplete.Select2QuerySetView
):
    def test_func(self):
        allowed_perms = [
            "algorithms.change_algorithm",
            "organizations.change_organization",
            "archives.change_archive",
            "reader_studies.change_readerstudy",
            "workstations.change_workstation",
            "algorithms.change_job",
        ]
        # TODO reduce number of queries
        return any(
            get_objects_for_user(user=self.request.user, perms=perm,).exists()
            for perm in allowed_perms
        )

    def get_queryset(self):
        qs = (
            get_user_model()
            .objects.order_by("username")
            .exclude(username=settings.ANONYMOUS_USER_NAME)
            .annotate(
                full_name=Concat(
                    "first_name",
                    Value(" "),
                    "last_name",
                    output_field=CharField(),
                )
            )
            .select_related("verification", "user_profile")
        )

        if self.q:
            qs = qs.filter(
                Q(username__icontains=self.q)
                | Q(email__icontains=self.q)
                | Q(full_name__icontains=self.q)
                | Q(verification__email=self.q)
            )

        return qs

    def get_result_label(self, result):

        try:
            is_verified = result.verification.is_verified
        except Verification.DoesNotExist:
            is_verified = False

        if is_verified:
            return format_html(
                '<img src="{}" width ="20" height ="20" style="vertical-align:top"> '
                "&nbsp; <b>{}</b> &nbsp; {} &nbsp;"
                '<i class="fas fa-user-check text-success" '
                'title="Verified email address at {}">',
                mark_safe(result.user_profile.get_mugshot_url()),
                result.get_username(),
                result.get_full_name().title(),
                result.verification.email.split("@")[1],
            )
        else:
            return format_html(
                '<img src="{}" width ="20" height ="20" style="vertical-align:top"> '
                "&nbsp; <b>{}</b> &nbsp; {}",
                mark_safe(result.user_profile.get_mugshot_url()),
                result.get_username(),
                result.get_full_name().title(),
            )
