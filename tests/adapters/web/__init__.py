from typing import Any, Dict, Optional, Tuple, Union

import ujson  # type: ignore

from wallet.validation import Validator


async def assert_valid_response(
    response,
    status: int = 200,
    content_type: Optional[str] = None,
    schema: Optional[Dict] = None,
) -> None:
    assert response.status == status

    if content_type:
        assert response.headers["Content-Type"] == content_type

    if schema:
        validator = Validator(schema=schema)

        data = await response.json()
        assert validator.validate_payload(data)


Payload = Dict[str, Any]
Headers = Dict[str, str]


def prepare_payload(
    data: Payload, headers: Optional[Headers] = None, json: bool = False
) -> Tuple[Union[str, Payload], Headers]:

    if headers is None:
        headers = {}

    payload: Union[str, Payload] = data
    if json:
        payload = ujson.dumps(data)
        headers["Content-Type"] = "application/json"

    return payload, headers
