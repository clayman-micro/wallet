from http import HTTPStatus

import pytest

from tests.web.handlers import assert_response_conforms_to
from wallet.web.schemas.accounts import AccountsResponseSchema


@pytest.mark.integration
async def test_success(client, get_token_for, user):
    """Successfully fetch accounts."""
    headers = {"X-ACCESS-TOKEN": get_token_for(user)}

    resp = await client.get("/api/accounts", headers=headers)  # act

    assert resp.status == HTTPStatus.OK
    await assert_response_conforms_to(response=resp, schema_cls=AccountsResponseSchema)
