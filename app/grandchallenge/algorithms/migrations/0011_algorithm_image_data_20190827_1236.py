# Generated by Django 2.2.4 on 2019-08-27 12:36
from django.db import migrations


def algorithm_container_images_to_algorithms_reverse(apps, schema_editor):
    # Reverse, create AlgorithmImage from Algorithm
    Algorithm = apps.get_model("algorithms", "Algorithm")
    AlgorithmImage = apps.get_model("algorithms", "AlgorithmImage")

    for a in Algorithm.objects.all():
        for im in a.algorithm_container_images.all():
            AlgorithmImage.objects.create(
                title=a.title,
                logo=a.logo,
                creator=im.creator,
                image=im.image,
                requires_gpu=im.requires_gpu,
                requires_gpu_memory_gb=im.requires_gpu_memory_gb,
                requires_memory_gb=im.requires_memory_gb,
                requires_cpu_cores=im.requires_cpu_cores,
                status=im.status,
            )


def algorithm_container_images_to_algorithms_forward(apps, schema_editor):
    # Forward, create Algorithm from AlgorithmImage
    from grandchallenge.algorithms.models import Algorithm

    AlgorithmImage = apps.get_model("algorithms", "AlgorithmImage")

    for ai in AlgorithmImage.objects.all():
        a = Algorithm.objects.create(
            title=ai.title,
            slug=ai.slug,
            logo=ai.logo,
            description=ai.description,
        )

        ai.algorithm_id = a.pk
        ai.save()

        if ai.creator:
            a.add_editor(ai.creator)

    for alg in Algorithm.objects.all():
        for ai in alg.algorithm_container_images.all():
            ai.assign_permissions()


class Migration(migrations.Migration):

    dependencies = [("algorithms", "0010_auto_20190827_1159")]

    operations = [
        migrations.RunPython(
            algorithm_container_images_to_algorithms_forward,
            algorithm_container_images_to_algorithms_reverse,
        )
    ]
