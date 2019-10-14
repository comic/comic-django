import pytest
from django.core.exceptions import ValidationError

from grandchallenge.workstation_configs.models import LookUpTable
from tests.workstation_config_tests.legacy_luts import LegacyLUT, LEGACY_LUTS


@pytest.mark.parametrize(
    "color,valid",
    (
        ("", False),
        ("[]", False),
        ("[1 2 3 4, 5 6 7 8]", True),
        ("[1 2 3 4, 5 6 7 8]\n\n", False),
    ),
)
def test_lut_color_regex(color, valid):
    lut = LookUpTable(color=color)
    err = None

    try:
        lut.clean_fields()
    except ValidationError as e:
        err = e

    assert ("color" in err.error_dict) != valid


@pytest.mark.parametrize("legacy_lut", LEGACY_LUTS)
def test_legacy_lut_conversion(legacy_lut: LegacyLUT):
    lut = LookUpTable(
        color=legacy_lut.lut_color,
        title=legacy_lut.title,
        alpha=legacy_lut.lut_alpha,
        color_invert=legacy_lut.lut_color_invert,
        alpha_invert=legacy_lut.lut_alpha_invert,
        range_min=legacy_lut.lut_range[0],
        range_max=legacy_lut.lut_range[1],
        relative=legacy_lut.lut_relative,
        color_interpolation=legacy_lut.color_interpolation.replace(
            "Interpolate", ""
        ),
        color_interpolation_invert=legacy_lut.color_interpolation_invert.replace(
            "Interpolate", ""
        ),
    )
    lut.full_clean()
