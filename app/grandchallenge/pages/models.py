import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Count, Max
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from grandchallenge.challenges.models import ComicSiteModel
from grandchallenge.core.templatetags.bleach import clean
from grandchallenge.core.utils.query import index
from grandchallenge.pages.substitutions import Substitution
from grandchallenge.subdomains.utils import reverse


class Page(ComicSiteModel):
    """Customisable content that belongs to a challenge."""

    UP = "UP"
    DOWN = "DOWN"
    FIRST = "FIRST"
    LAST = "LAST"
    order = models.IntegerField(
        editable=False,
        default=1,
        help_text="Determines order in which page appear in site menu",
    )
    display_title = models.CharField(
        max_length=255,
        default="",
        blank=True,
        help_text=(
            "On pages and in menu items, use this text. Spaces and special "
            "chars allowed here. Optional field. If emtpy, title is used"
        ),
    )
    hidden = models.BooleanField(
        default=False, help_text="Do not display this page in site menu"
    )
    html = models.TextField(blank=True, default="")

    def save(self, *args, **kwargs):
        # when saving for the first time only, put this page last in order
        if not self.id:
            # get max value of order for current pages.
            try:
                max_order = Page.objects.filter(
                    challenge=self.challenge
                ).aggregate(Max("order"))
            except ObjectDoesNotExist:
                max_order = None
            try:
                self.order = max_order["order__max"] + 1
            except TypeError:
                self.order = 1
        super().save(*args, **kwargs)

    def cleaned_html(self):
        out = clean(self.html)

        if "project_statistics" in out:
            users = self.challenge.get_participants().select_related(
                "user_profile"
            )
            country_data = (
                users.exclude(user_profile__country="")
                .annotate(country_count=Count("user_profile__country"))
                .order_by("-country_count")
                .values_list("user_profile__country", "country_count")
            )
            content = render_to_string(
                "grandchallenge/partials/geochart.html",
                {
                    "user_count": users.count(),
                    "country_data": json.dumps(
                        [["Country", "#Participants"]] + list(country_data)
                    ),
                },
            )

            s = Substitution(
                tag_name="project_statistics",
                content=f"<h1>Statistics</h1>{content}",
            )
            out = s.replace(out)

        # self.html has been cleaned at this point, and nothing new introduced by
        # the substitutions so this is safe
        return mark_safe(out)

    def move(self, move):
        if move == self.UP:
            mm = Page.objects.get(
                challenge=self.challenge, order=self.order - 1
            )
            mm.order += 1
            mm.save()
            self.order -= 1
            self.save()
        elif move == self.DOWN:
            mm = Page.objects.get(
                challenge=self.challenge, order=self.order + 1
            )
            mm.order -= 1
            mm.save()
            self.order += 1
            self.save()
        elif move == self.FIRST:
            pages = Page.objects.filter(challenge=self.challenge)
            idx = index(pages, self)
            pages[idx].order = pages[0].order - 1
            pages = sorted(pages, key=lambda page: page.order)
            self.normalize_page_order(pages)
        elif move == self.LAST:
            pages = Page.objects.filter(challenge=self.challenge)
            idx = index(pages, self)
            pages[idx].order = pages[len(pages) - 1].order + 1
            pages = sorted(pages, key=lambda page: page.order)
            self.normalize_page_order(pages)

    @staticmethod
    def normalize_page_order(pages):
        """Make sure order in pages Queryset starts at 1 and increments 1 at
        every page. Saves all pages

        """
        for idx, page in enumerate(pages):
            page.order = idx + 1
            page.save()

    def get_absolute_url(self):
        url = reverse(
            "pages:detail",
            kwargs={
                "challenge_short_name": self.challenge.short_name,
                "page_title": self.title,
            },
        )
        return url

    class Meta(ComicSiteModel.Meta):
        """special class holding meta info for this class"""

        # make sure a single site never has two pages with the same name
        # because page names are used as keys in urls
        unique_together = (("challenge", "title"),)
        # when getting a list of these objects this ordering is used
        ordering = ["challenge", "order"]


class ErrorPage(Page):
    """
    Just the same as a Page, just that it does not display an edit button as
    admin
    """

    is_error_page = True

    def can_be_viewed_by(self, user):
        """Allow all users to view ErrorPages."""
        return True

    class Meta:
        abstract = True  # error pages should only be generated on the fly
