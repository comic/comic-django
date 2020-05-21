import os
import tarfile
import zipfile
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Sequence, Tuple
from uuid import UUID

from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from grandchallenge.algorithms.models import Job
from grandchallenge.cases.emails import send_failed_file_import
from grandchallenge.cases.image_builders import ImageBuilderResult
from grandchallenge.cases.image_builders.dicom import image_builder_dicom
from grandchallenge.cases.image_builders.fallback import image_builder_fallback
from grandchallenge.cases.image_builders.metaio_mhd_mha import (
    image_builder_mhd,
)
from grandchallenge.cases.image_builders.tiff import image_builder_tiff
from grandchallenge.cases.log import logger
from grandchallenge.cases.models import (
    FolderUpload,
    Image,
    ImageFile,
    RawImageFile,
    RawImageUploadSession,
)
from grandchallenge.jqfileupload.widgets.uploader import (
    NotFoundError,
    StagedAjaxFile,
)


class ProvisioningError(Exception):
    pass


def _populate_tmp_dir(tmp_dir, upload_session):
    session_files = upload_session.rawimagefile_set.all()
    session_files, duplicates = remove_duplicate_files(session_files)

    for duplicate in duplicates:  # type: RawImageFile
        duplicate.error = "Filename not unique"
        saf = StagedAjaxFile(duplicate.staged_file_id)
        duplicate.staged_file_id = None
        saf.delete()
        duplicate.consumed = False
        duplicate.save()

    populate_provisioning_directory(session_files, tmp_dir)
    extract_files(tmp_dir)


def populate_provisioning_directory(
    raw_files: Sequence[RawImageFile], provisioning_dir: Path
):
    """
    Provisions provisioning_dir with the files associated using the given
    list of RawImageFile objects.

    Parameters
    ----------
    raw_files:
        The list of RawImageFile that should be saved in the target
        directory.

    provisioning_dir: Path
        The path where to copy the files.

    Raises
    ------
    ProvisioningError:
        Raised when not all files could be copied to the provisioning directory.
    """
    provisioning_dir = Path(provisioning_dir)

    def copy_to_tmpdir(image_file: RawImageFile):
        staged_file = StagedAjaxFile(image_file.staged_file_id)
        if not staged_file.exists:
            raise ValueError(
                f"staged file {image_file.staged_file_id} does not exist"
            )

        with open(provisioning_dir / staged_file.name, "wb") as dest_file:
            with staged_file.open() as src_file:
                buffer_size = 0x10000
                first = True
                buffer = b""
                while first or (len(buffer) >= buffer_size):
                    first = False
                    buffer = src_file.read(buffer_size)
                    dest_file.write(buffer)

    exceptions_raised = 0
    for raw_file in raw_files:
        try:
            copy_to_tmpdir(raw_file)
        except Exception:
            logger.exception(
                f"populate_provisioning_directory exception "
                f"for file: '{raw_file.filename}'"
            )
            exceptions_raised += 1

    if exceptions_raised > 0:
        raise ProvisioningError(
            f"{exceptions_raised} errors occurred during provisioning of the "
            f"image construction directory"
        )


@transaction.atomic
def store_image(
    image: Image,
    all_image_files: Sequence[ImageFile],
    all_folder_uploads: Sequence[FolderUpload],
):
    """
    Stores an image in the database in a single transaction (or fails
    accordingly). Associated image files are extracted from the
    all_image_files argument and stored together with the image itself
    in a single transaction.

    Parameters
    ----------
    image: :class:`Image`
        The image to store. The actual image files that are stored are extracted
        from the second argument.

    all_image_files: list of :class:`ImageFile`
        An unordered list of ImageFile objects that might or might not belong
        to the image provided as the first argument. The function automatically
        extracts related images from the all_image_files argument to store
        alongside the given image.

    all_folder_uploads: list of :class:`FolderUpload`
        An unordered list of FolderUpload objects that might or might not belong
        to the image provided as the first argument. The function automatically
        extracts related folders from the all_folder_uploads argument to store
        alongside the given image. The files in this folder will be saved to
        the storage but not added to the database.
    """
    associated_files = [_if for _if in all_image_files if _if.image == image]
    image.save()
    for af in associated_files:
        af.save()

    associated_folders = [
        _if for _if in all_folder_uploads if _if.image == image
    ]
    for af in associated_folders:
        af.save()


IMAGE_BUILDER_ALGORITHMS = [
    image_builder_mhd,
    image_builder_dicom,
    image_builder_tiff,
    image_builder_fallback,
]


def remove_duplicate_files(
    session_files: Sequence[RawImageFile],
) -> Tuple[Sequence[RawImageFile], Sequence[RawImageFile]]:
    """
    Filters the given sequence of RawImageFile objects and removes all files
    that have a nun-unqie filename.

    Parameters
    ----------
    session_files: Sequence[RawImageFile]
        List of RawImageFile objects thats filenames should be checked for
        uniqueness.

    Returns
    -------
    Two Sequence[RawImageFile]. The first sequence is the filtered session_files
    list, the second list is a list of duplicates that were removed.
    """
    filename_lookup = {}
    duplicates = []
    for file in session_files:
        if file.filename in filename_lookup:
            duplicates.append(file)

            looked_up_file = filename_lookup[file.filename]
            if looked_up_file is not None:
                duplicates.append(looked_up_file)
                filename_lookup[file.filename] = None
        else:
            filename_lookup[file.filename] = file
    return (
        tuple(x for x in filename_lookup.values() if x is not None),
        tuple(duplicates),
    )


def _check_sanity(info, is_tar, path):
    # Check tar files for symlinks and reject upload session if any.
    if is_tar:
        if info.issym() or info.islnk():
            raise ValidationError("(Symbolic) links are not allowed.")
    # Also check for max path length, drop folders when path is too long
    filename_attr = "name" if is_tar else "filename"
    while len(os.path.join(path, getattr(info, filename_attr))) > 4095:
        filename = getattr(info, filename_attr)
        filename = os.path.join(
            *Path(filename).parts[1 : len(Path(filename).parts)]
        )
        setattr(info, filename_attr, filename)


def extract(file, path, is_tar=False):
    """
    Extracts all files in `file` to `path`.

    Parameters
    ----------
    file:
        A zip or tar file.
    path:
        The path to which the contents of `file` are to be extracted.

    """
    list_func = file.getmembers if is_tar else file.infolist
    filename_attr = "name" if is_tar else "filename"
    is_dir_func = "isdir" if is_tar else "is_dir"
    for info in sorted(list_func(), key=lambda k: getattr(k, filename_attr)):
        # Skip directories
        if getattr(info, is_dir_func)():
            continue

        _check_sanity(info, is_tar, path)
        file.extract(info, path)


def check_compressed_and_extract(file_path, target_path, checked_paths=None):
    """
    Checks if `file_path` is a zip or tar file and if so, extracts it.

    Parameters
    ----------
    file_path:
        The file path to be checked and possibly extracted.
    target_path:
        The path to which the contents of `file_path` are to be extracted.
    checked_paths:
        Files that have already been extracted.
    """

    def extract_file(file_path):
        if tarfile.is_tarfile(file_path):
            with tarfile.open(file_path) as tf:
                extract(tf, target_path, is_tar=True)
                file_path.unlink()
                return True
        elif zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path) as zf:
                extract(zf, target_path)
                file_path.unlink()
                return True
        return False

    if checked_paths is None:
        checked_paths = []
    if file_path in checked_paths:
        return
    checked_paths.append(file_path)

    extracted = extract_file(file_path)

    # check zips in zips
    if extracted:
        for root, _, files in os.walk(target_path):
            for file in files:
                check_compressed_and_extract(
                    Path(os.path.join(root, file)), root, checked_paths
                )


def extract_files(source_path: Path):
    checked_paths = []
    for file_path in source_path.iterdir():
        check_compressed_and_extract(file_path, source_path, checked_paths)


@shared_task
def build_images(upload_session_uuid: UUID):
    """
    Task which analyzes an upload session and attempts to extract and store
    detected images assembled from files uploaded in the image session.

    The task updates the state-filed of the associated
    :class:`RawImageUploadSession` to indicate if it is running or has finished
    computing.

    The task also updates the consumed field of the associated
    :class:`RawImageFile` to indicate whether it has been processed or not.

    Results are stored in:
    - `RawImageUploadSession.error_message` if a general error occurred during
        processing.
    - The `RawImageFile.error` field of associated `RawImageFile` objects,
        in case files could not be processed.

    The operation of building images will delete associated `StagedAjaxFile`s
    of analyzed images in order to free up space on the server (only done if the
    function does not error out).

    If a job fails due to a RawImageUploadSession.DoesNotExist error, the
    job is queued for a retry (max 15 times).

    Parameters
    ----------
    upload_session_uuid: UUID
        The uuid of the upload sessions that should be analyzed.
    """
    upload_session = RawImageUploadSession.objects.get(
        pk=upload_session_uuid
    )  # type: RawImageUploadSession

    if (
        upload_session.status != upload_session.REQUEUED
        or upload_session.rawimagefile_set.filter(consumed=True).exists()
    ):
        upload_session.status = upload_session.FAILURE
        upload_session.error_message = (
            "Not starting job as some files were already consumed."
        )
        upload_session.save()
        return

    upload_session.status = upload_session.STARTED
    upload_session.save()

    with TemporaryDirectory(prefix="construct_image_volumes-") as tmp_dir:
        tmp_dir = Path(tmp_dir)

        try:
            _populate_tmp_dir(tmp_dir, upload_session)
            _handle_raw_image_files(tmp_dir, upload_session)
        except ProvisioningError as e:
            upload_session.error_message = str(e)
            upload_session.status = upload_session.FAILURE
            upload_session.save()
            return
        except Exception:
            upload_session.error_message = "An unknown error occurred"
            upload_session.status = upload_session.FAILURE
            upload_session.save()
            raise
        else:
            upload_session.status = upload_session.SUCCESS
            upload_session.save()


def _handle_raw_image_files(tmp_dir, upload_session):
    unconsumed_files = [
        Path(d[0]).joinpath(f) for d in os.walk(tmp_dir) for f in d[2]
    ]
    session_files = [
        RawImageFile.objects.get_or_create(
            filename=str(f.relative_to(tmp_dir)),
            upload_session=upload_session,
        )[0]
        for f in unconsumed_files
    ]

    filepath_lookup = {
        raw_image_file.staged_file_id
        and os.path.join(
            tmp_dir, StagedAjaxFile(raw_image_file.staged_file_id).name
        )
        or os.path.join(tmp_dir, raw_image_file.filename): raw_image_file
        for raw_image_file in session_files
    }

    collected_images = []
    collected_associated_files = []
    collected_associated_folders = []

    for algorithm in IMAGE_BUILDER_ALGORITHMS:
        algorithm_result = algorithm(
            unconsumed_files, session_id=upload_session.pk
        )  # type: ImageBuilderResult
        collected_images += list(algorithm_result.new_images)
        collected_associated_files += list(algorithm_result.new_image_files)

        collected_associated_folders += list(
            algorithm_result.new_folder_upload
        )

        for filepath in algorithm_result.consumed_files:
            if filepath in unconsumed_files:
                unconsumed_files.remove(filepath)
                raw_image = filepath_lookup[
                    str(filepath)
                ]  # type: RawImageFile
                raw_image.error = None
                raw_image.consumed = True
                raw_image.save()

        for (filepath, msg,) in algorithm_result.file_errors_map.items():
            if filepath in unconsumed_files:
                raw_image = filepath_lookup[
                    str(filepath)
                ]  # type: RawImageFile
                raw_image.error = raw_image.error or ""
                raw_image.error += f"{msg}\n"
                raw_image.consumed = False
                raw_image.save()

    for image in collected_images:
        image.origin = upload_session
        store_image(
            image, collected_associated_files, collected_associated_folders,
        )
    _handle_image_relations(
        collected_images=collected_images, upload_session=upload_session
    )

    _handle_unconsumed_files(
        filepath_lookup=filepath_lookup,
        unconsumed_files=unconsumed_files,
        upload_session=upload_session,
    )

    _delete_session_files(
        session_files=session_files, upload_session=upload_session
    )


def _handle_image_relations(*, collected_images, upload_session):
    if upload_session.imageset:
        upload_session.imageset.images.add(*collected_images)

    if upload_session.annotationset:
        upload_session.annotationset.images.add(*collected_images)

    if upload_session.algorithm_image:
        for image in collected_images:
            Job.objects.create(
                creator=upload_session.creator,
                algorithm_image=upload_session.algorithm_image,
                image=image,
            )

    if upload_session.algorithm_result:
        upload_session.algorithm_result.images.add(*collected_images)

    if upload_session.reader_study:
        upload_session.reader_study.images.add(*collected_images)

    if upload_session.archive:
        upload_session.archive.images.add(*collected_images)


def _handle_unconsumed_files(
    *, filepath_lookup, unconsumed_files, upload_session
):
    errors = []
    for unconsumed_filepath in unconsumed_files:
        raw_file = filepath_lookup[str(unconsumed_filepath)]
        error = raw_file.error or ""
        raw_file.error = (
            f"File could not be processed by any image builder:\n\n{error}"
        )
        errors.append(error)
        raw_file.save()

    if unconsumed_files:
        upload_session.error_message = (
            f"{len(unconsumed_files)} file(s) could not be imported"
        )

        if upload_session.creator and upload_session.creator.email:
            send_failed_file_import(errors, upload_session)


def _delete_session_files(*, session_files, upload_session):
    dicom_group = Group.objects.get(
        name=settings.DICOM_DATA_CREATORS_GROUP_NAME
    )
    users = dicom_group.user_set.values_list("username", flat=True)
    for file in session_files:
        try:
            if file.staged_file_id:
                saf = StagedAjaxFile(file.staged_file_id)

                if not file.consumed and upload_session.archive:
                    # Keep unconsumed archive files
                    saf.staged_files.update(
                        timeout=timezone.now() + timedelta(days=90)
                    )
                    continue

                if (
                    not file.consumed
                    and Path(file.filename).suffix == ".dcm"
                    and getattr(file.creator, "username", None) in users
                ):
                    saf.staged_files.update(
                        timeout=timezone.now() + timedelta(days=90)
                    )
                    continue

                file.staged_file_id = None
                saf.delete()
            file.save()
        except NotFoundError:
            pass
