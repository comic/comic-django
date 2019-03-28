from django.contrib.auth.models import User
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from guardian.shortcuts import get_objects_for_user
from rest_framework import generics, status
from rest_framework.response import Response
from grandchallenge.subdomains.utils import reverse
from grandchallenge.core.permissions.mixins import UserIsStaffMixin
from grandchallenge.worklists.models import Worklist, WorklistSet
from grandchallenge.worklists.serializers import (
    WorklistSerializer,
    WorklistSetSerializer,
)
from grandchallenge.worklists.forms import (
    WorklistCreateForm,
    WorklistUpdateForm,
    WorklistSetCreateForm,
    WorklistSetUpdateForm,
)

""" Worklist API Endpoints """


class WorklistTable(generics.ListCreateAPIView):
    serializer_class = WorklistSerializer

    def get_queryset(self):
        queryset = Worklist.objects.filter(set__user=self.request.user)
        return queryset


class WorklistRecord(generics.RetrieveUpdateDestroyAPIView):
    queryset = Worklist.objects.all()
    serializer_class = WorklistSerializer

    def retrieve(self, request, *args, **kwargs):
        user = request.user

        if not user.has_perm("view_worklist", self.Worklist):
            return Response(status=status.HTTP_403_FORBIDDEN)

        serialized = WorklistSetSerializer(self.Worklist)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        # assign_perm("change_worklist", set.user, self)
        return super.update(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = request.user

        if not user.has_perm("delete_worklist", self.Worklist):
            return Response(status=status.HTTP_403_FORBIDDEN)

        self.Worklist.delete()
        return Response(status=status.HTTP_200_OK)


""" WorklistSet API Endpoints """


class WorklistSetTable(generics.ListCreateAPIView):
    serializer_class = WorklistSetSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        if "title" not in data or len(data["title"]) == 0:
            return Response(
                "Title field is not set.", status=status.HTTP_400_BAD_REQUEST
            )

        if "user" in data and len(data["user"]) > 0:
            user = User.objects.get(pk=data["user"])

        set = WorklistSet.objects.create(title=data["title"], user=user)
        serializer = WorklistSetSerializer(set)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = WorklistSet.objects.filter(user=self.request.user)
        return queryset


class WorklistSetRecord(generics.RetrieveUpdateDestroyAPIView):
    queryset = WorklistSet.objects.all()
    serializer_class = WorklistSetSerializer

    def update(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        if "title" not in data or len(data["title"]) == 0:
            return Response(
                "Title field is not set.", status=status.HTTP_400_BAD_REQUEST
            )

        if "user" in data:
            user = User.objects.get(pk=data["user"])

        set = WorklistSet.objects.get(pk=self.WorklistSet.pk)
        set.title = data["title"]
        set.user = user
        set.save()

        serialized = WorklistSetSerializer(set)
        return Response(serialized.data, status=status.HTTP_200_OK)


""" Worklist Forms Views """


# class WorklistCreateView(UserIsStaffMixin, CreateView):
class WorklistCreateView(CreateView):
    model = Worklist
    form_class = WorklistCreateForm

    def get_success_url(self):
        return reverse("worklists:list-display")


class WorklistRemoveView(UserIsStaffMixin, DeleteView):
    model = Worklist
    template_name = "worklists/worklist_remove_form.html"

    def get_success_url(self):
        return reverse("worklists:list-display")


class WorklistUpdateView(UserIsStaffMixin, UpdateView):
    model = Worklist
    form_class = WorklistUpdateForm

    def get_success_url(self):
        return reverse("worklists:list-display")


class WorklistDisplayView(UserIsStaffMixin, ListView):
    model = Worklist
    paginate_by = 100
    template_name = "worklists/worklist_display_form.html"


""" WorklistSet Forms Views """


class WorklistSetCreateView(UserIsStaffMixin, CreateView):
    model = WorklistSet
    form_class = WorklistSetCreateForm

    def get_success_url(self):
        return reverse("worklists:set-display")


class WorklistSetRemoveView(UserIsStaffMixin, DeleteView):
    model = WorklistSet
    template_name = "worklists/worklistset_remove_form.html"

    def get_success_url(self):
        return reverse("worklists:set-display")


class WorklistSetUpdateView(UserIsStaffMixin, UpdateView):
    model = WorklistSet
    form_class = WorklistSetUpdateForm

    def get_success_url(self):
        return reverse("worklists:set-display")


class WorklistSetDisplayView(UserIsStaffMixin, ListView):
    model = WorklistSet
    paginate_by = 100
    template_name = "worklists/worklistset_display_form.html"
