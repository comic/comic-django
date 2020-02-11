from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate


def init_users_groups(*_, **__):
    from django.contrib.auth.models import Group
    from guardian.utils import get_anonymous_user

    anon = get_anonymous_user()

    g_reg_anon, _ = Group.objects.get_or_create(
        name=settings.REGISTERED_AND_ANON_USERS_GROUP_NAME
    )
    anon.groups.add(g_reg_anon)

    g_reg, _ = Group.objects.get_or_create(
        name=settings.REGISTERED_USERS_GROUP_NAME
    )
    anon.groups.remove(g_reg)


class CoreConfig(AppConfig):
    name = "grandchallenge.core"

    def ready(self):
        post_migrate.connect(init_users_groups, sender=self)

        # noinspection PyUnresolvedReferences
        import grandchallenge.core.signals  # noqa: F401
