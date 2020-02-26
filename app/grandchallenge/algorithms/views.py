import logging

from dal import autocomplete
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import (
    NON_FIELD_ERRORS,
    PermissionDenied,
    ValidationError,
)
from django.forms.utils import ErrorList
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.functional import cached_property
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)
from guardian.core import ObjectPermissionChecker
from guardian.mixins import (
    LoginRequiredMixin,
    PermissionListMixin,
    PermissionRequiredMixin as ObjectPermissionRequiredMixin,
)
from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_guardian.filters import ObjectPermissionsFilter

from grandchallenge.algorithms.forms import (
    AlgorithmForm,
    AlgorithmImageForm,
    AlgorithmImageUpdateForm,
    EditorsForm,
    PermissionRequestUpdateForm,
    ResultForm,
    UsersForm,
)
from grandchallenge.algorithms.models import (
    Algorithm,
    AlgorithmImage,
    AlgorithmPermissionRequest,
    Job,
    Result,
)
from grandchallenge.algorithms.serializers import (
    AlgorithmImageSerializer,
    AlgorithmSerializer,
    JobSerializer,
    ResultSerializer,
)
from grandchallenge.cases.forms import UploadRawImagesForm
from grandchallenge.cases.models import RawImageUploadSession
from grandchallenge.core.permissions.mixins import UserIsNotAnonMixin
from grandchallenge.subdomains.utils import reverse

logger = logging.getLogger(__name__)


class AlgorithmCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Algorithm
    form_class = AlgorithmForm
    permission_required = (
        f"{Algorithm._meta.app_label}.add_{Algorithm._meta.model_name}"
    )

    def form_valid(self, form):
        response = super().form_valid(form=form)
        self.object.add_editor(self.request.user)
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs


class AlgorithmList(PermissionListMixin, ListView):
    model = Algorithm
    permission_required = {
        f"{Algorithm._meta.app_label}.view_{Algorithm._meta.model_name}"
    }
    ordering = "-created"


class AlgorithmDetail(ObjectPermissionRequiredMixin, DetailView):
    model = Algorithm
    permission_required = (
        f"{Algorithm._meta.app_label}.view_{Algorithm._meta.model_name}"
    )
    raise_exception = True

    def on_permission_check_fail(self, request, response, obj=None):
        response = self.get(request)
        return response

    def check_permissions(self, request):
        """
        Checks if *request.user* has all permissions returned by
        *get_required_permissions* method.

        :param request: Original request.
        """
        try:
            return super().check_permissions(request)
        except PermissionDenied:
            return redirect(
                "algorithms:permission-request-create", slug=self.object.slug
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = UsersForm()
        form.fields["action"].initial = UsersForm.REMOVE
        context.update({"form": form})

        pending_permission_requests = AlgorithmPermissionRequest.objects.filter(
            algorithm=self.get_object(),
            status=AlgorithmPermissionRequest.PENDING,
        ).count()
        context.update(
            {"pending_permission_requests": pending_permission_requests}
        )

        return context


class AlgorithmUpdate(
    LoginRequiredMixin, ObjectPermissionRequiredMixin, UpdateView
):
    model = Algorithm
    form_class = AlgorithmForm
    permission_required = (
        f"{Algorithm._meta.app_label}.change_{Algorithm._meta.model_name}"
    )
    raise_exception = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs


class AlgorithmUserAutocomplete(
    LoginRequiredMixin, UserPassesTestMixin, autocomplete.Select2QuerySetView
):
    def test_func(self):
        group_pks = (
            Algorithm.objects.all()
            .select_related("editors_group")
            .values_list("editors_group__pk", flat=True)
        )
        return (
            self.request.user.is_superuser
            or self.request.user.groups.filter(pk__in=group_pks).exists()
        )

    def get_queryset(self):
        qs = (
            get_user_model()
            .objects.all()
            .order_by("username")
            .exclude(username=settings.ANONYMOUS_USER_NAME)
        )

        if self.q:
            qs = qs.filter(username__istartswith=self.q)

        return qs


class AlgorithmUserGroupUpdateMixin(
    LoginRequiredMixin,
    ObjectPermissionRequiredMixin,
    SuccessMessageMixin,
    FormView,
):
    template_name = "algorithms/algorithm_user_groups_form.html"
    permission_required = (
        f"{Algorithm._meta.app_label}.change_{Algorithm._meta.model_name}"
    )
    raise_exception = True

    def get_permission_object(self):
        return self.algorithm

    @property
    def algorithm(self):
        return get_object_or_404(Algorithm, slug=self.kwargs["slug"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {"object": self.algorithm, "role": self.get_form().role}
        )
        return context

    def get_success_url(self):
        return self.algorithm.get_absolute_url()

    def form_valid(self, form):
        form.add_or_remove_user(algorithm=self.algorithm)
        return super().form_valid(form)


class EditorsUpdate(AlgorithmUserGroupUpdateMixin):
    form_class = EditorsForm
    success_message = "Editors successfully updated"


class UsersUpdate(AlgorithmUserGroupUpdateMixin):
    form_class = UsersForm
    success_message = "Users successfully updated"


class AlgorithmImageCreate(
    LoginRequiredMixin, ObjectPermissionRequiredMixin, CreateView
):
    model = AlgorithmImage
    form_class = AlgorithmImageForm
    permission_required = (
        f"{Algorithm._meta.app_label}.change_{Algorithm._meta.model_name}"
    )
    raise_exception = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    @property
    def algorithm(self):
        return get_object_or_404(Algorithm, slug=self.kwargs["slug"])

    def get_permission_object(self):
        return self.algorithm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.algorithm = self.algorithm

        uploaded_file = form.cleaned_data["chunked_upload"][0]
        form.instance.staged_image_uuid = uploaded_file.uuid

        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({"algorithm": self.algorithm})
        return context


class AlgorithmImageDetail(
    LoginRequiredMixin, ObjectPermissionRequiredMixin, DetailView
):
    model = AlgorithmImage
    permission_required = f"{AlgorithmImage._meta.app_label}.view_{AlgorithmImage._meta.model_name}"
    raise_exception = True


class AlgorithmImageUpdate(
    LoginRequiredMixin, ObjectPermissionRequiredMixin, UpdateView
):
    model = AlgorithmImage
    form_class = AlgorithmImageUpdateForm
    permission_required = f"{AlgorithmImage._meta.app_label}.change_{AlgorithmImage._meta.model_name}"
    raise_exception = True

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({"algorithm": self.object.algorithm})
        return context


class AlgorithmExecutionSessionCreate(
    LoginRequiredMixin, ObjectPermissionRequiredMixin, CreateView,
):
    model = RawImageUploadSession
    form_class = UploadRawImagesForm
    template_name = "algorithms/algorithm_execution_session_create.html"
    permission_required = (
        f"{Algorithm._meta.app_label}.execute_{Algorithm._meta.model_name}"
    )
    raise_exception = True

    @property
    def algorithm(self) -> Algorithm:
        return get_object_or_404(Algorithm, slug=self.kwargs["slug"])

    def get_permission_object(self):
        return self.algorithm

    def get_initial(self):
        if self.algorithm.latest_ready_image is None:
            raise Http404()
        return super().get_initial()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.algorithm_image = self.algorithm.latest_ready_image
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({"algorithm": self.algorithm})
        return context

    def get_success_url(self):
        return reverse(
            "algorithms:execution-session-detail",
            kwargs={"slug": self.kwargs["slug"], "pk": self.object.pk},
        )


class AlgorithmExecutionSessionDetail(
    LoginRequiredMixin, ObjectPermissionRequiredMixin, DetailView
):
    model = RawImageUploadSession
    template_name = "algorithms/executionsession_detail.html"
    permission_required = "cases.view_rawimageuploadsession"
    raise_exception = True

    @property
    def algorithm(self) -> Algorithm:
        return get_object_or_404(Algorithm, slug=self.kwargs["slug"])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({"algorithm": self.algorithm})
        return context


class AlgorithmResultsList(PermissionListMixin, ListView):
    model = Result
    permission_required = (
        f"{Result._meta.app_label}.view_{Result._meta.model_name}"
    )

    @cached_property
    def algorithm(self):
        return get_object_or_404(Algorithm, slug=self.kwargs["slug"])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        checker = ObjectPermissionChecker(self.request.user)
        checker.prefetch_perms(context["object_list"])

        change_result = {}

        for result in context["object_list"]:
            change_result[str(result.pk)] = checker.has_perm(
                "change_result", result
            )

        context.update(
            {"algorithm": self.algorithm, "change_result": change_result}
        )

        return context

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.filter(
            job__algorithm_image__algorithm=self.algorithm
        ).select_related("job")


class AlgorithmResultUpdate(
    LoginRequiredMixin, ObjectPermissionRequiredMixin, UpdateView
):
    model = Result
    form_class = ResultForm
    permission_required = (
        f"{Result._meta.app_label}.change_{Result._meta.model_name}"
    )
    raise_exception = True

    def get_success_url(self):
        return reverse(
            "algorithms:results-list",
            kwargs={"slug": self.object.job.algorithm_image.algorithm.slug},
        )


class AlgorithmViewSet(ReadOnlyModelViewSet):
    queryset = Algorithm.objects.all()
    serializer_class = AlgorithmSerializer
    permission_classes = [DjangoObjectPermissions]
    filter_backends = [ObjectPermissionsFilter]


class AlgorithmImageViewSet(ReadOnlyModelViewSet):
    queryset = AlgorithmImage.objects.all()
    serializer_class = AlgorithmImageSerializer
    permission_classes = [DjangoObjectPermissions]
    filter_backends = [ObjectPermissionsFilter]


class JobViewSet(ReadOnlyModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [DjangoObjectPermissions]
    filter_backends = [ObjectPermissionsFilter]


class ResultViewSet(ReadOnlyModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [DjangoObjectPermissions]
    filter_backends = [ObjectPermissionsFilter]


class AlgorithmPermissionRequestCreate(
    UserIsNotAnonMixin, SuccessMessageMixin, CreateView
):
    model = AlgorithmPermissionRequest
    fields = ()

    @property
    def algorithm(self):
        return get_object_or_404(Algorithm, slug=self.kwargs["slug"])

    def get_success_url(self):
        return self.algorithm.get_absolute_url()

    def get_success_message(self, cleaned_data):
        return self.object.status_to_string()

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.algorithm = self.algorithm
        try:
            redirect = super().form_valid(form)
            return redirect

        except ValidationError as e:
            form._errors[NON_FIELD_ERRORS] = ErrorList(e.messages)
            return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        permission_request = AlgorithmPermissionRequest.objects.filter(
            algorithm=self.algorithm, user=self.request.user
        ).first()
        context.update(
            {
                "permission_request": permission_request,
                "algorithm": self.algorithm,
            }
        )
        return context


class AlgorithmPermissionRequestList(ObjectPermissionRequiredMixin, ListView):
    model = AlgorithmPermissionRequest
    permission_required = (
        f"{Algorithm._meta.app_label}.change_{Algorithm._meta.model_name}"
    )
    raise_exception = True

    @property
    def algorithm(self):
        return get_object_or_404(Algorithm, slug=self.kwargs["slug"])

    def get_permission_object(self):
        return self.algorithm

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = (
            queryset.filter(algorithm=self.algorithm)
            .exclude(status=AlgorithmPermissionRequest.ACCEPTED)
            .select_related("user__user_profile")
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"algorithm": self.algorithm})
        return context


class AlgorithmPermissionRequestUpdate(SuccessMessageMixin, UpdateView):
    model = AlgorithmPermissionRequest
    form_class = PermissionRequestUpdateForm

    @property
    def algorithm(self) -> Algorithm:
        return get_object_or_404(Algorithm, slug=self.kwargs["slug"])

    def form_valid(self, form):
        permission_request = self.get_object()
        user = permission_request.user
        form.instance.user = user
        if (
            not self.algorithm.is_editor(self.request.user)
            and not self.algorithm.is_user(user)
            and not self.algorithm.is_editor(user)
        ):
            form.instance.status = AlgorithmPermissionRequest.PENDING
        try:
            redirect = super().form_valid(form)
            return redirect

        except ValidationError as e:
            form._errors[NON_FIELD_ERRORS] = ErrorList(e.messages)
            return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "permission_request": self.get_object(),
                "algorithm": self.algorithm,
            }
        )
        return context

    def get_success_message(self, cleaned_data):
        if not self.algorithm.is_editor(self.request.user):
            return "You request for access has been sent to editors"
        return "Permission request successfully updated"

    def get_success_url(self):
        if not self.algorithm.is_editor(self.request.user):
            return reverse("algorithms:list")
        return reverse(
            "algorithms:permission-request-list",
            kwargs={"slug": self.algorithm.slug},
        )
