from typing import Union

from django import template
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from grandchallenge.subdomains.utils import reverse

register = template.Library()


@register.filter
def user_profile_link(user: Union[AbstractUser, None]) -> str:
    verified = ""

    if user:
        username = user.username
        profile_url = reverse(
            "userena_profile_detail", kwargs={"username": user.username}
        )
        mugshot = format_html(
            (
                '<img class="mugshot" loading="lazy" src="{0}" '
                'alt="User Mugshot" '
                # Match the "fa-lg" class style
                'style="height: 1.33em; vertical-align: -25%;"/>'
            ),
            user.profile.get_mugshot_url(),
        )

        try:
            if user.verification.is_verified:
                verified = mark_safe(
                    '<i class="fas fa-user-check text-success" '
                    'title="Verified User"></i>'
                )
        except ObjectDoesNotExist:
            # No verification request
            pass
    else:
        username = "Unknown"
        profile_url = "#"
        mugshot = mark_safe('<i class="fas fa-user fa-lg"></i>')

    return format_html(
        '<a href="{0}">{1}</a>&nbsp;<a href="{0}">{2}</a>&nbsp;{3}',
        profile_url,
        mugshot,
        username,
        verified,
    )


@register.filter
def user_profile_link_username(username: str) -> str:
    User = get_user_model()  # noqa: N806
    return user_profile_link(User.objects.get(username=username))
