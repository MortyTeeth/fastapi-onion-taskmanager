def remove_keys(d: dict, keys_to_remove: list[str]) -> dict:
    return {k: v for k, v in d.items() if k not in keys_to_remove}


from contextlib import nullcontext
from typing import Any, Dict, Optional


class RequestTestCase:
    """
    Represents a single API request test case.
    """

    def __init__(
            self,
            url: str,
            data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            expected_status: int = 200,
            expected_data: Optional[Dict[str, Any]] = None,
            expected_error: Optional[Any] = None,
    ):
        self.url = url
        self.data = data or {}
        self.headers = headers or {}
        self.expected_status = expected_status
        self.expected_data = expected_data or {}
        self.expected_error = expected_error or nullcontext()


from typing import Dict, List, Optional
from httpx import Response


def prepare_payload(response: Response, exclude_fields: Optional[List[str]] = None) -> Dict:
    """
    Prepares API response payload for comparison in tests.

    :param response: HTTPX Response object.
    :param exclude_fields: List of fields to remove from the response (e.g., ['id']).
    :return: Dict with cleaned response data.
    """
    data = response.json()
    exclude_fields = exclude_fields or []

    if isinstance(data, list):
        return [
            {k: v for k, v in item.items() if k not in exclude_fields} for item in data
        ]
    else:
        return {k: v for k, v in data.items() if k not in exclude_fields}
