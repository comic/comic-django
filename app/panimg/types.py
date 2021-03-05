from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set

from grandchallenge.cases.models import FolderUpload, ImageFile
from panimg.models import PanImg


@dataclass
class ImageBuilderResult:
    new_images: Set[PanImg]
    new_image_files: Set[ImageFile]
    new_folders: Set[FolderUpload]
    consumed_files: Set[Path]
    file_errors: Dict[Path, str]


@dataclass
class PanimgResult(ImageBuilderResult):
    file_errors: Dict[Path, List[str]]
