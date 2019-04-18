import pytest
from tests.worklists_tests.factories import WorklistFactory
from tests.api_utils import assert_api_crud


@pytest.mark.django_db
@pytest.mark.parametrize(
    "table_reverse, expected_table, factory, invalid_fields",
    [("api:worklists", "Worklist Table", WorklistFactory, ["user_id"])],
)
def test_api_pages(
    client, table_reverse, expected_table, factory, invalid_fields
):
    assert_api_crud(
        client, table_reverse, expected_table, factory, invalid_fields
    )
