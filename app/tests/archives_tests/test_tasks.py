import pytest

from grandchallenge.archives.tasks import add_images_to_archive
from tests.archives_tests.factories import ArchiveFactory
from tests.factories import ImageFactory


@pytest.mark.django_db
def test_add_images_is_idempotent():
    archive = ArchiveFactory()
    image = ImageFactory()

    assert archive.images.count() == 0

    add_images_to_archive(
        upload_session_pk=image.origin.pk, archive_pk=archive.pk
    )

    assert archive.images.count() == 1

    add_images_to_archive(
        upload_session_pk=image.origin.pk, archive_pk=archive.pk
    )

    assert archive.images.count() == 1
