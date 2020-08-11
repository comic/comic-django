from io import StringIO

import pytest
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from guardian.core import ObjectPermissionChecker

from grandchallenge.annotations.models import PolygonAnnotationSet
from grandchallenge.retina_core.management.commands.migratelesionnames import (
    migrate_annotations,
)
from grandchallenge.retina_core.management.commands.setannotationpermissions import (
    ANNOTATION_MODELS,
    SUCCESS_TEXT,
    WARNING_TEXT,
)
from tests.annotations_tests.factories import PolygonAnnotationSetFactory
from tests.factories import ImageFactory, ImagingModalityFactory


@pytest.mark.django_db
class TestCommand:
    nr_of_default_permissions = (
        4  # nr of default_permissions in each model is fixed right now
    )
    nr_of_mlps = len(ANNOTATION_MODELS) * nr_of_default_permissions
    nr_of_olps = (
        22 * nr_of_default_permissions
    )  # 22 == nr of annotation models in AnnotationSet fixture

    def test_setannotationpermissions_no_annotations(self):
        out = StringIO()
        call_command("setannotationpermissions", stdout=out)
        output = out.getvalue()
        assert WARNING_TEXT.format(self.nr_of_mlps, "assigned") in output

    def test_setannotationpermissions_no_annotations_remove(self):
        out = StringIO()
        call_command("setannotationpermissions", remove=True, stdout=out)
        output = out.getvalue()
        assert WARNING_TEXT.format(self.nr_of_mlps, "removed") in output

    def test_setannotationpermissions_no_retina_grader_annotations(
        self, annotation_set
    ):
        out = StringIO()
        call_command("setannotationpermissions", stdout=out)
        output = out.getvalue()
        assert WARNING_TEXT.format(self.nr_of_mlps, "assigned") in output

    def test_setannotationpermissions(self, annotation_set):
        annotation_set.grader.groups.add(
            Group.objects.get(name=settings.RETINA_GRADERS_GROUP_NAME)
        )
        out = StringIO()
        call_command("setannotationpermissions", stdout=out)
        output = out.getvalue()
        assert (
            SUCCESS_TEXT.format(self.nr_of_mlps, self.nr_of_olps, "assigned")
            in output
        )

    def test_setannotationpermissions_remove(self, annotation_set):
        annotation_set.grader.groups.add(
            Group.objects.get(name=settings.RETINA_GRADERS_GROUP_NAME)
        )
        out = StringIO()
        call_command("setannotationpermissions", remove=True, stdout=out)
        output = out.getvalue()
        assert (
            SUCCESS_TEXT.format(self.nr_of_mlps, self.nr_of_olps, "removed")
            in output
        )

    def test_setannotationpermissions_sets_correct_permissions(
        self, annotation_set
    ):
        admins_group = Group.objects.get(
            name=settings.RETINA_ADMINS_GROUP_NAME
        )
        graders_group = Group.objects.get(
            name=settings.RETINA_GRADERS_GROUP_NAME
        )
        annotation_set.grader.groups.add(graders_group)
        call_command("setannotationpermissions")

        checker = ObjectPermissionChecker(annotation_set.grader)
        group_perms = Permission.objects.filter(
            group=admins_group
        ).values_list("codename", flat=True)

        for annotation_model in ANNOTATION_MODELS:
            annotation_codename = annotation_model._meta.model_name
            for annotation in annotation_model.objects.all():
                perms = checker.get_perms(annotation)
                for permission_type in annotation._meta.default_permissions:
                    assert f"{permission_type}_{annotation_codename}" in perms

                for permission_type in annotation._meta.default_permissions:
                    assert (
                        f"{permission_type}_{annotation_codename}"
                        in group_perms
                    )

    def test_setannotationpermissions_removes_correct_permissions(
        self, annotation_set
    ):
        admins_group = Group.objects.get(
            name=settings.RETINA_ADMINS_GROUP_NAME
        )
        graders_group = Group.objects.get(
            name=settings.RETINA_GRADERS_GROUP_NAME
        )
        annotation_set.grader.groups.add(graders_group)
        call_command("setannotationpermissions")

        call_command("setannotationpermissions", remove=True)

        checker = ObjectPermissionChecker(annotation_set.grader)
        group_perms = Permission.objects.filter(
            group=admins_group, content_type__app_label="annotations"
        ).values_list("codename", flat=True)
        assert len(group_perms) == 0

        for annotation_model in ANNOTATION_MODELS:
            for annotation in annotation_model.objects.all():
                perms = checker.get_perms(annotation)
                assert len(perms) == 0


@pytest.mark.django_db
class TestMigratelesionnamesCommand:
    def test_testmigratelesionnames_no_match(self):
        annotation = PolygonAnnotationSetFactory(name="No match")
        result = migrate_annotations(PolygonAnnotationSet.objects.all())
        assert result["translated"] == 0
        assert result["no_match"] == [annotation.id]

    def test_testmigratelesionnames_no_match_enface(self):
        annotation = PolygonAnnotationSetFactory(
            name="amd_present::Drusen and drusen like structures::Conical drusen"
        )
        result = migrate_annotations(PolygonAnnotationSet.objects.all())
        assert result["translated"] == 0
        assert result["enface_no_match"] == [annotation.id]

    def test_testmigratelesionnames_no_match_oct(self):
        image = ImageFactory(modality=ImagingModalityFactory(modality="OCT"))
        annotation = PolygonAnnotationSetFactory(
            name="amd_present::Pigment changes & RPE degeneration::Increased pigmentation",
            image=image,
        )
        result = migrate_annotations(PolygonAnnotationSet.objects.all())
        assert result["translated"] == 0
        assert result["oct_no_match"] == [annotation.id]

    def test_testmigratelesionnames_no_match_oct_boolean(self):
        image = ImageFactory(modality=ImagingModalityFactory(modality="OCT"))
        annotation = PolygonAnnotationSetFactory(
            name="other_present::Vascular::Branch retinal artery occlusion",
            image=image,
        )
        result = migrate_annotations(PolygonAnnotationSet.objects.all())
        assert result["translated"] == 0
        assert result["boolean_oct_no_match"] == [annotation.id]

    def test_testmigratelesionnames_already_migrated(self):
        image = ImageFactory(modality=ImagingModalityFactory(modality="OCT"))
        PolygonAnnotationSetFactory(
            name="retina::oct::macular::Drusen", image=image
        )
        PolygonAnnotationSetFactory(
            name="retina::enface::rf_present::Hard drusen"
        )
        result = migrate_annotations(PolygonAnnotationSet.objects.all())
        assert result["translated"] == 0
        assert result["already_translated"] == 2

    def test_testmigratelesionnames_correctly_migrated(self):
        image = ImageFactory(modality=ImagingModalityFactory(modality="OCT"))
        annotation_oct = PolygonAnnotationSetFactory(
            name="amd_present::Drusen and drusen like structures::Hard Drusen",
            image=image,
        )
        annotation_enface = PolygonAnnotationSetFactory(
            name="drusen and drusen like structures::hard drusen"
        )
        result = migrate_annotations(PolygonAnnotationSet.objects.all())
        assert result["translated"] == 2
        annotation_enface.refresh_from_db()
        assert (
            annotation_enface.name == "retina::enface::rf_present::Hard drusen"
        )
        annotation_oct.refresh_from_db()
        assert annotation_oct.name == "retina::oct::macular::Drusen"

    def test_testmigratelesionnames_combined(self):
        image = ImageFactory(modality=ImagingModalityFactory(modality="OCT"))
        annotation_oct = PolygonAnnotationSetFactory(
            name="amd_present::Drusen and drusen like structures::Hard Drusen",
            image=image,
        )
        annotation_enface = PolygonAnnotationSetFactory(
            name="drusen and drusen like structures::hard drusen"
        )
        PolygonAnnotationSetFactory(
            name="retina::oct::macular::Drusen", image=image
        )
        PolygonAnnotationSetFactory(
            name="retina::enface::rf_present::Hard drusen"
        )
        annotation_oct_no_match_boolean = PolygonAnnotationSetFactory(
            name="other_present::Vascular::Branch retinal artery occlusion",
            image=image,
        )
        annotation_oct_no_match = PolygonAnnotationSetFactory(
            name="amd_present::Pigment changes & RPE degeneration::Increased pigmentation",
            image=image,
        )
        annotation_enface_no_match = PolygonAnnotationSetFactory(
            name="amd_present::Drusen and drusen like structures::Conical drusen"
        )
        annotation_no_match = PolygonAnnotationSetFactory(name="No match")

        result = migrate_annotations(PolygonAnnotationSet.objects.all())
        assert result["translated"] == 2
        assert result["already_translated"] == 2
        assert result["boolean_oct_no_match"] == [
            annotation_oct_no_match_boolean.id
        ]
        assert result["oct_no_match"] == [annotation_oct_no_match.id]
        assert result["enface_no_match"] == [annotation_enface_no_match.id]
        assert result["no_match"] == [annotation_no_match.id]
        annotation_enface.refresh_from_db()
        assert (
            annotation_enface.name == "retina::enface::rf_present::Hard drusen"
        )
        annotation_oct.refresh_from_db()
        assert annotation_oct.name == "retina::oct::macular::Drusen"
