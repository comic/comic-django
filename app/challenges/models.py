import copy
import datetime
import logging
import os

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.validators import validate_slug, MinLengthValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from guardian.utils import get_anonymous_user

from comicsite.core.urlresolvers import reverse
from comicsite.validators import validate_nounderscores

logger = logging.getLogger("django")


class ProjectLink(object):
    """ Metadata about a single project: url, event etc. Used as the shared
    class for both external challenges and projects hosted on comic so they can
    be shown on the projectlinks overview page

    """
    # Using dict instead of giving a lot of fields to this object because the
    # former is easier to work with
    defaults = {
        "abreviation": "",
        "title": "",
        "description": "",
        "URL": "",
        "submission URL": "",
        "event name": "",
        "year": "",
        "event URL": "",
        "image URL": "",
        "website section": "",
        "overview article url": "",
        "overview article journal": "",
        "overview article citations": "",
        "overview article date": "",
        "submission deadline": "",
        "workshop date": "",
        "open for submission": "",
        "dataset downloads": "",
        "registered teams": "",
        "submitted results": "",
        "last submission date": "",
        "hosted on comic": False,
        "project type": "",
    }
    # css selector used to designate a project as still open
    UPCOMING = "challenge_upcoming"

    def __init__(self, params, date=""):
        self.params = copy.deepcopy(self.defaults)
        self.params.update(params)
        # add date in addition to datestring already in dict, to make sorting
        # easier.
        if date == "":
            self.date = self.determine_project_date()
        else:
            self.date = date
        self.params["year"] = self.date.year

    def determine_project_date(self):
        """ Try to find the date for this project. Return default
        date if nothing can be parsed.

        """
        if self.params["hosted on comic"]:
            if self.params["workshop date"]:
                date = self.to_datetime(self.params["workshop date"])
            else:
                date = ""
        else:
            datestr = self.params["workshop date"]
            # this happens when excel says its a number. I dont want to force
            # the excel file to be clean, so deal with it here.
            if type(datestr) == float:
                datestr = str(datestr)[0:8]
            try:
                date = timezone.make_aware(
                    datetime.datetime.strptime(datestr, "%Y%m%d"),
                    timezone.get_default_timezone(),
                )
            except ValueError:
                logger.warning(
                    "could not parse date '%s' from xls line starting with "
                    "'%s'. Returning default date 2013-01-01" %
                    (datestr, self.params["abreviation"])
                )
                date = ""
        if date == "":
            # If you cannot find the exact date for a project,
            # use date created
            if self.params["hosted on comic"]:
                return self.params["created at"]

            # If you cannot find the exact date, try to get at least the year
            # right. again do not throw errors, excel can be dirty
            year = int(self.params["year"])
            try:
                date = timezone.make_aware(
                    datetime.datetime(year, 1, 1),
                    timezone.get_default_timezone(),
                )
            except ValueError:
                logger.warning(
                    "could not parse year '%f' from xls line starting with "
                    "'%s'. Returning default date 2013-01-01" %
                    (year, self.params["abreviation"])
                )
                date = timezone.make_aware(
                    datetime.datetime(2013, 1, 1),
                    timezone.get_default_timezone(),
                )
        return date

    def find_link_class(self):
        """ Get css classes to give to this projectlink.
        For filtering and sorting project links, we discern upcoming, active
        and inactive projects. Determiniation of upcoming/active/inactive is
        described in column 'website section' in grand-challenges xls.
        For projects hosted on comic, determine this automatically based on
        associated workshop date. If a comicsite has an associated workshop
        which is in the future, make it upcoming, otherwise active

        """
        linkclass = ComicSite.CHALLENGE_ACTIVE
        # for project hosted on comic, try to find upcoming automatically
        if self.params["hosted on comic"]:
            linkclass = self.params["project type"]
            if self.date > self.to_datetime(datetime.datetime.today()):
                linkclass += " " + self.UPCOMING
        else:
            # else use the explicit setting in xls
            section = self.params["website section"].lower()
            if section == "upcoming challenges":
                linkclass = ComicSite.CHALLENGE_ACTIVE + " " + self.UPCOMING
            elif section == "active challenges":
                linkclass = ComicSite.CHALLENGE_ACTIVE
            elif section == "past challenges":
                linkclass = ComicSite.CHALLENGE_INACTIVE
            elif section == "data publication":
                linkclass = ComicSite.DATA_PUB
        return linkclass

    @staticmethod
    def to_datetime(date):
        """ add midnight to a date to make it a datetime because I cannot
        compare these two types directly. Also add offset awareness to easily
        compare with other django datetimes.
        """
        dt = datetime.datetime(date.year, date.month, date.day)
        return timezone.make_aware(dt, timezone.get_default_timezone())

    def is_hosted_on_comic(self):
        return self.params["hosted on comic"]


class ComicSiteManager(models.Manager):
    """ adds some tabel level functions for getting ComicSites from db. """

    def non_hidden(self):
        """ like all(), but only return ComicSites for which hidden=false"""
        return self.filter(hidden=False)

    def get_queryset(self):
        return super(ComicSiteManager, self).get_queryset()


class ComicSite(models.Model):
    """
    A collection of HTML pages using a certain skin. Pages can be browsed and
    edited.
    """
    public_folder = "public_html"
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    short_name = models.SlugField(
        max_length=50,
        default="",
        help_text=(
            "short name used in url, specific css, files etc. "
            "No spaces allowed"
        ),
        validators=[
            validate_nounderscores, validate_slug, MinLengthValidator(1)
        ],
        unique=True,
    )
    skin = models.CharField(
        max_length=225,
        default=public_folder + "/project.css",
        help_text="css file to include throughout this"
        " project. relative to project data folder",
    )
    description = models.CharField(
        max_length=1024,
        default="",
        blank=True,
        help_text="Short summary of " "this project, max 1024 characters.",
    )
    title = models.CharField(
        max_length=64,
        blank=True,
        default='',
        help_text=(
            'The name of the challenge that is displayed on the All Challenges'
            ' page. If this is blank the short name of the challenge will be '
            'used.'
        ),
    )
    logo = models.CharField(
        max_length=255,
        default=public_folder + "/logo.png",
        help_text="100x100 pixel image file to use as logo"
        " in projects overview. Relative to project datafolder",
    )
    header_image = models.CharField(
        max_length=255,
        blank=True,
        help_text="optional 658 pixel wide Header image which will "
        "appear on top of each project page top of each "
        "project. "
        "Relative to project datafolder. Suggested default:" +
        public_folder +
        "/header.png",
    )
    hidden = models.BooleanField(
        default=True,
        help_text="Do not display this Project in any public overview",
    )
    hide_signin = models.BooleanField(
        default=False,
        help_text="Do no show the Sign in / Register link on any page",
    )
    hide_footer = models.BooleanField(
        default=False,
        help_text=(
            "Do not show the general links or "
            "the grey divider line in page footers"
        ),
    )
    disclaimer = models.CharField(
        max_length=2048,
        default="",
        blank=True,
        null=True,
        help_text=(
            "Optional text to show on each page in the project. "
            "For showing 'under construction' type messages"
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    workshop_date = models.DateField(
        null=True,
        blank=True,
        help_text=(
            "Date on which the workshop belonging to this project will be held"
        ),
    )
    event_name = models.CharField(
        max_length=1024,
        default="",
        blank=True,
        null=True,
        help_text="The name of the event the workshop will be held at",
    )
    event_url = models.URLField(
        blank=True,
        null=True,
        help_text="Website of the event which will host the workshop",
    )
    CHALLENGE_ACTIVE = 'challenge_active'
    CHALLENGE_INACTIVE = 'challenge_inactive'
    DATA_PUB = 'data_pub'
    is_open_for_submissions = models.BooleanField(
        default=False,
        help_text=(
            "This project currently accepts new submissions. "
            "Affects listing in projects overview"
        ),
    )
    submission_page_name = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text=(
            "If the project allows submissions, there will be a link in "
            "projects overview going directly to you "
            "project/<submission_page_name>/. If empty, the projects main "
            "page will be used instead"
        ),
    )
    number_of_submissions = models.IntegerField(
        blank=True,
        null=True,
        help_text=(
            "The number of submissions have been evalutated for this project"
        ),
    )
    last_submission_date = models.DateField(
        null=True,
        blank=True,
        help_text="When was the last submission evaluated?",
    )
    offers_data_download = models.BooleanField(
        default=False,
        help_text=(
            "This project currently accepts new submissions. Affects listing "
            "in projects overview"
        ),
    )
    number_of_downloads = models.IntegerField(
        blank=True,
        null=True,
        help_text=(
            "How often has the dataset for this project been downloaded?"
        ),
    )
    publication_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL of a publication describing this project",
    )
    publication_journal_name = models.CharField(
        max_length=225,
        blank=True,
        null=True,
        help_text=(
            "If publication was in a journal, please list the journal name "
            "here We use <a target='new' "
            "href='https://www.ncbi.nlm.nih.gov/nlmcatalog/journals'>PubMed "
            "journal abbreviations</a> format"
        ),
    )
    require_participant_review = models.BooleanField(
        default=False,
        help_text=(
            "If ticked, new participants need to be approved by project "
            "admins before they can access restricted pages. If not ticked, "
            "new users are allowed access immediately"
        ),
    )
    use_registration_page = models.BooleanField(
        default=True,
        help_text='If true, show a registration page on the challenge site.',
    )
    registration_page_text = models.TextField(
        default='',
        blank=True,
        help_text=(
            'The text to use on the registration page, you could include '
            'a data usage agreement here. You can use HTML markup here.'
        ),
    )
    use_evaluation = models.BooleanField(
        default=False,
        help_text=(
            "If true, use the automated evaluation system. See the evaluation "
            "page created in the Challenge site."
        ),
    )
    admins_group = models.OneToOneField(
        Group,
        null=True,
        editable=False,
        on_delete=models.CASCADE,
        related_name='admins_of_challenge',
    )
    participants_group = models.OneToOneField(
        Group,
        null=True,
        editable=False,
        on_delete=models.CASCADE,
        related_name='participants_of_challenge',
    )
    objects = ComicSiteManager()

    def __str__(self):
        """ string representation for this object"""
        return self.short_name

    def clean(self):
        """ clean method is called automatically for each save in admin"""
        pass

    # TODO check whether short name is really clean and short!
    def delete(self, using=None, keep_parents=False):
        """ Ensure that there are no orphans """
        self.admins_group.delete(using)
        self.participants_group.delete(using)
        super().delete(using, keep_parents)

    def get_project_data_folder(self):
        """ Full path to root folder for all data belonging to this project
        """
        return os.path.join(settings.MEDIA_ROOT, self.short_name)

    def upload_dir(self):
        """Full path to get and put secure uploaded files. Files here cannot be
        viewed directly by url
        """
        return os.path.join(settings.MEDIA_ROOT, self.upload_dir_rel())

    def upload_dir_rel(self):
        """Path to get and put secure uploaded files relative to MEDIA_ROOT

        """
        return os.path.join(self.short_name, "uploads")

    def public_upload_dir(self):
        """Full path to get and put uploaded files. These files can be served
        to anyone without checking

         """
        return os.path.join(settings.MEDIA_ROOT, self.public_upload_dir_rel())

    def public_upload_dir_rel(self):
        """ Path to public uploaded files, relative to MEDIA_ROOT

        """
        return os.path.join(self.short_name, settings.COMIC_PUBLIC_FOLDER_NAME)

    def admin_group_name(self):
        """
        returns the name of the admin group which should have all rights to
        this ComicSite instance
        """
        return self.short_name + "_admins"

    def participants_group_name(self):
        """
        returns the name of the participants group, which should have some
        rights to this ComicSite instance
        """
        return self.short_name + "_participants"

    def get_relevant_perm_groups(self):
        """
        Return all auth groups which are directly relevant for this ComicSite.
        This method is used for showin permissions for these groups, even
        if none are defined
        """
        groups = Group.objects.filter(
            Q(name=settings.EVERYONE_GROUP_NAME) |
            Q(pk=self.admins_group.pk) |
            Q(pk=self.participants_group.pk)
        )
        return groups

    def is_admin(self, user):
        """
        is user in the admins group for the comicsite to which this object
        belongs? superuser always passes
        """
        if user.is_superuser:
            return True

        if user.groups.filter(pk=self.admins_group.pk).exists():
            return True

        else:
            return False

    def is_participant(self, user):
        """
        is user in the participants group for the comicsite to which this
        object belong? superuser always passes
        """
        if user.is_superuser:
            return True

        if user.groups.filter(pk=self.participants_group.pk).exists():
            return True

        else:
            return False

    def get_admins(self):
        """ Return all users that are in this comicsites admin group """
        return self.admins_group.user_set.all()

    def get_participants(self):
        """ Return all participants of this challenge """
        return self.participants_group.user_set.all()

    def get_absolute_url(self):
        """ With this method, admin will show a 'view on site' button """
        url = reverse('challenge-homepage', args=[self.short_name])
        return url

    def to_projectlink(self):
        """
        Return a ProjectLink representation of this comicsite, to show in an
        overview page listing all projects
        """
        thumb_image_url = reverse(
            'project_serve_file', args=[self.short_name, self.logo]
        )
        args = {
            "abreviation": self.short_name,
            "title": self.title if self.title else self.short_name,
            "description": self.description,
            "URL": reverse('challenge-homepage', args=[self.short_name]),
            "download URL": "",
            "submission URL": self.get_submission_url(),
            "event name": self.event_name,
            "year": "",
            "event URL": self.event_url,
            "image URL": self.logo,
            "thumb_image_url": thumb_image_url,
            "website section": "active challenges",
            "overview article url": self.publication_url,
            "overview article journal": self.publication_journal_name,
            "overview article citations": "",
            "overview article date": "",
            "submission deadline": "",
            "workshop date": self.workshop_date,
            "open for submission": "yes" if self.is_open_for_submissions else "no",
            "data download": "yes" if self.offers_data_download else "no",
            "dataset downloads": self.number_of_downloads,
            "registered teams": "",
            "submitted results": self.number_of_submissions,
            "last submission date": self.last_submission_date,
            "hosted on comic": True,
            "created at": self.created_at,
        }
        projectlink = ProjectLink(args)
        return projectlink

    def get_submission_url(self):
        """ What url can you go to to submit for this project? """
        url = reverse('challenge-homepage', args=[self.short_name])
        if self.submission_page_name:
            if self.submission_page_name.startswith(
                "http://"
            ) or self.submission_page_name.startswith(
                "https://"
            ):
                # the url in the submission page box is a full url
                return self.submission_page_name

            else:
                page = self.submission_page_name
                if not page.endswith("/"):
                    page += "/"
                url += page
        return url

    def add_participant(self, user):
        if user != get_anonymous_user():
            user.groups.add(self.participants_group)
        else:
            raise ValueError('You cannot add the anonymous user to this group')

    def remove_participant(self, user):
        user.groups.remove(self.participants_group)

    def add_admin(self, user):
        if user != get_anonymous_user():
            user.groups.add(self.admins_group)
        else:
            raise ValueError('You cannot add the anonymous user to this group')

    def remove_admin(self, user):
        user.groups.remove(self.admins_group)

    class Meta:
        verbose_name = "challenge"
        verbose_name_plural = "challenges"
        db_table = "comicmodels_comicsite"
