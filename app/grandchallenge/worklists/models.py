from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import CharField
from guardian.shortcuts import assign_perm
from grandchallenge.core.models import UUIDModel
from grandchallenge.cases.models import Image


class WorklistSet(UUIDModel):
    """
    Represents a collection of worklists for a single user.
    """

    title = CharField(max_length=255)
    user = models.OneToOneField(
        User, blank=True, null=True, on_delete=models.CASCADE
    )

    def get_children(self):
        return Worklist.objects.filter(set=self.pk)

    def save(self, *args, **kwargs):
        created = self._state.adding
        super().save(*args, **kwargs)

        if created:
            worklist_group = Group.objects.get(
                name=settings.WORKLIST_ACCESS_GROUP_NAME
            )

            if self.user is not None:
                self.user.groups.add(worklist_group)
                assign_perm("view_worklistset", self.user, self)
                assign_perm("change_worklistset", self.user, self)
                assign_perm("delete_worklistset", self.user, self)
            else:
                assign_perm("view_worklistset", worklist_group, self)

    def __str__(self):
        return "{} ({})".format(self.title, str(self.id))


class Worklist(UUIDModel):
    """
    Represents a collection of images.
    """

    title = CharField(max_length=255)
    set = models.ForeignKey(WorklistSet, null=False, on_delete=models.CASCADE)
    images = models.ManyToManyField(
        to=Image, related_name="worklist", blank=True
    )

    def save(self, *args, **kwargs):
        created = self._state.adding
        super().save(*args, **kwargs)

        if created:
            set = WorklistSet.objects.get(pk=self.set.id)
            if set.user is not None:
                assign_perm("view_worklist", set.user, self)
                assign_perm("change_worklist", set.user, self)
                assign_perm("delete_worklist", set.user, self)
            else:
                worklist_group = Group.objects.get(
                    name=settings.WORKLIST_ACCESS_GROUP_NAME
                )
                assign_perm("view_worklist", worklist_group, self)

    def __str__(self):
        return "{} ({})".format(self.title, str(self.id))

    class Meta(UUIDModel.Meta):
        unique_together = ("title", "set")
