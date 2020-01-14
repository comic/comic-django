import re
from typing import Tuple


class Substitution:
    def __init__(
        self,
        *,
        tag_name: str,
        content: str,
        markers: Tuple[str, str] = ("{%", "%}"),
    ):

        self._tag_name = tag_name.strip()
        self._replacement = content.strip()
        self._markers = [re.escape(m) for m in markers]

    @property
    def regex(self) -> str:
        return rf"{self._markers[0]}\s*{self._tag_name}\s*{self._markers[1]}"

    def replace(self, s: str) -> str:
        return re.sub(self.regex, self._replacement, s)
