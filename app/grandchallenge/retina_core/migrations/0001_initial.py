# Generated by Django 2.1.3 on 2018-12-07 15:50

from django.db import migrations

# from django.contrib.auth import get_user_model
from django.conf import settings

#
# def copy_ada_annotations_to_demo_forward(apps, schema_editor):
#     """
#     This migration copies all annotations that belong to grader with username 'ada' to the demo user. This is used for
#     debugging purposes. It has to be run manually when annotation data has been imported.
#     """
#     Measurement = apps.get_model("annotations", "MeasurementAnnotation")
#     BooleanClassification = apps.get_model(
#         "annotations", "BooleanClassificationAnnotation"
#     )
#     PolygonAnnotationSet = apps.get_model(
#         "annotations", "PolygonAnnotationSet"
#     )
#     LandmarkAnnotationSet = apps.get_model(
#         "annotations", "LandmarkAnnotationSet"
#     )
#     ETDRSGrid = apps.get_model("annotations", "ETDRSGridAnnotation")
#
#     for model in (
#         Measurement,
#         BooleanClassification,
#         PolygonAnnotationSet,
#         LandmarkAnnotationSet,
#         ETDRSGrid,
#     ):
#         for obj in model.objects.filter(grader__username="ada"):
#             children = []
#             if type(obj) == PolygonAnnotationSet:
#                 # copy children
#                 children = obj.singlepolygonannotation_set.all()
#             if type(obj) == LandmarkAnnotationSet:
#                 children = obj.singlelandmarkannotation_set.all()
#
#             obj.grader_id = get_user_model().objects.get(username="demo").id
#             obj.pk = None
#             obj.save()
#
#             for child in children:
#                 child.pk = None
#                 child.annotation_set = obj
#                 child.save()
#
#
# def copy_ada_annotations_to_demo_backward(apps, schema_editor):
#     """
#     Removes ALL annotations that belong to demo user.
#     """
#     Measurement = apps.get_model("annotations", "MeasurementAnnotation")
#     BooleanClassification = apps.get_model(
#         "annotations", "BooleanClassificationAnnotation"
#     )
#     PolygonAnnotationSet = apps.get_model(
#         "annotations", "PolygonAnnotationSet"
#     )
#     LandmarkAnnotationSet = apps.get_model(
#         "annotations", "LandmarkAnnotationSet"
#     )
#     ETDRSGrid = apps.get_model("annotations", "ETDRSGridAnnotation")
#
#     for model in (
#         Measurement,
#         BooleanClassification,
#         PolygonAnnotationSet,
#         LandmarkAnnotationSet,
#         ETDRSGrid,
#     ):
#         model.objects.filter(grader__username="demo").delete()


def create_retina_groups_and_user_forward(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Group = apps.get_model("auth", "Group")

    # Create retina import user
    User.objects.create_user(settings.RETINA_IMPORT_USER_NAME)

    # Create retina admin and grader groups
    Group.objects.create(name=settings.RETINA_GRADERS_GROUP_NAME)
    Group.objects.create(name=settings.RETINA_ADMINS_GROUP_NAME)


def create_retina_groups_and_user_backward(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Group = apps.get_model("auth", "Group")

    # Remove retina import user
    User.objects.get(username=settings.RETINA_IMPORT_USER_NAME).delete()

    # Remove retina admin and grader groups
    Group.objects.get(name=settings.RETINA_GRADERS_GROUP_NAME).delete()
    Group.objects.get(name=settings.RETINA_ADMINS_GROUP_NAME).delete()


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        # migrations.RunPython(
        #     copy_ada_annotations_to_demo_forward,
        #     copy_ada_annotations_to_demo_backward,
        # ),
        migrations.RunPython(
            create_retina_groups_and_user_forward,
            create_retina_groups_and_user_backward,
        )
    ]
