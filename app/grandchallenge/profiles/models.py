from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from guardian.shortcuts import assign_perm
from userena.managers import ASSIGNED_PERMISSIONS
from userena.models import UserenaBaseProfile

from grandchallenge.core.utils import disable_for_loaddata
from grandchallenge.subdomains.utils import reverse


class UserProfile(UserenaBaseProfile):
    user = models.OneToOneField(
        get_user_model(),
        unique=True,
        verbose_name=_("user"),
        related_name="user_profile",
        on_delete=models.CASCADE,
    )

    institution = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    country = CountryField()
    website = models.CharField(max_length=150, blank=True)

    def get_absolute_url(self):
        return reverse(
            "userena_profile_detail", kwargs={"username": self.user.username}
        )


@disable_for_loaddata
def create_user_profile(instance, created, *_, **__):
    if created:
        profile = UserProfile.objects.create(user=instance)

        for perm in ASSIGNED_PERMISSIONS["profile"]:
            assign_perm(perm[0], instance, profile)

        for perm in ASSIGNED_PERMISSIONS["user"]:
            assign_perm(perm[0], instance, instance)


post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)
