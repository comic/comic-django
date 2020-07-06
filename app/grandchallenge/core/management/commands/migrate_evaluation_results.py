from django.core.management import BaseCommand
from django.core.paginator import Paginator

from grandchallenge.evaluation.models import Result


class Command(BaseCommand):
    def handle(self, *args, **options):
        results = (
            Result.objects.all().order_by("created").prefetch_related("job")
        )
        paginator = Paginator(results, 100)

        for idx in paginator.page_range:
            print(f"Page {idx} of {paginator.num_pages}")

            page = paginator.page(idx)

            for result in page.object_list:
                if result.job:
                    job = result.job
                    job.published = result.published
                    job.save()

                    job.create_result(result=result.metrics)

                    result.job = None
                    result.save()
                else:
                    print(f"Skipping result {result.pk}")
