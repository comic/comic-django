import os

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.validators import validate_slug, MinLengthValidator
from django.db import models
from django.db.models import Q
from guardian.shortcuts import assign_perm, remove_perm
from guardian.utils import get_anonymous_user

from comicsite.core.urlresolvers import reverse
from comicsite.utils.links import ProjectLink
from comicsite.validators import validate_nounderscores


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


class ComicSiteModel(models.Model):
    """
    An object which can be shown or used in the comicsite framework.
    This base class should handle common functions such as authorization.
    """
    title = models.SlugField(max_length=64, blank=False)
    challenge = models.ForeignKey(
        ComicSite, help_text="To which comicsite does this object belong?"
    )
    ALL = 'ALL'
    REGISTERED_ONLY = 'REG'
    ADMIN_ONLY = 'ADM'
    PERMISSIONS_CHOICES = (
        (ALL, 'All'),
        (REGISTERED_ONLY, 'Registered users only'),
        (ADMIN_ONLY, 'Administrators only'),
    )
    PERMISSION_WEIGHTS = ((ALL, 0), (REGISTERED_ONLY, 1), (ADMIN_ONLY, 2))
    permission_lvl = models.CharField(
        max_length=3, choices=PERMISSIONS_CHOICES, default=ALL
    )

    def __str__(self):
        """ string representation for this object"""
        return self.title

    def can_be_viewed_by(self, user):
        """ boolean, is user allowed to view this? """
        # check whether everyone is allowed to view this. Anymous user is the
        # only member of group 'everyone' for which permissions can be set
        anonymous_user = get_anonymous_user()
        if anonymous_user.has_perm("view_ComicSiteModel", self):
            return True

        else:
            # if not everyone has access,
            # check whether given user has permissions
            return user.has_perm("view_ComicSiteModel", self)

    def setpermissions(self, lvl):
        """ Give the right groups permissions to this object
            object needs to be saved before setting perms"""
        admingroup = self.challenge.admins_group
        participantsgroup = self.challenge.participants_group
        everyonegroup = Group.objects.get(name=settings.EVERYONE_GROUP_NAME)
        self.persist_if_needed()
        if lvl == self.ALL:
            assign_perm("view_ComicSiteModel", admingroup, self)
            assign_perm("view_ComicSiteModel", participantsgroup, self)
            assign_perm("view_ComicSiteModel", everyonegroup, self)
        elif lvl == self.REGISTERED_ONLY:
            assign_perm("view_ComicSiteModel", admingroup, self)
            assign_perm("view_ComicSiteModel", participantsgroup, self)
            remove_perm("view_ComicSiteModel", everyonegroup, self)
        elif lvl == self.ADMIN_ONLY:
            assign_perm("view_ComicSiteModel", admingroup, self)
            remove_perm("view_ComicSiteModel", participantsgroup, self)
            remove_perm("view_ComicSiteModel", everyonegroup, self)
        else:
            raise ValueError(
                f"Unknown permissions level '{lvl}'. "
                "I don't know which groups to give permissions to this object"
            )

    def persist_if_needed(self):
        """
        setting permissions needs a persisted object. This method makes sure.
        """
        if not self.id:
            super(ComicSiteModel, self).save()

    def save(self, *args, **kwargs):
        self.setpermissions(self.permission_lvl)
        super(ComicSiteModel, self).save()

    class Meta:
        abstract = True
        permissions = (("view_ComicSiteModel", "Can view Comic Site Model"),)


