from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlencode

if TYPE_CHECKING:
    from pydantic import HttpUrl


class UrlBuilder:
    def __init__(
        self,
        base_url: HttpUrl,
        api_prefix: str,
        v1_prefix: str,
    ) -> None:
        self._base = str(base_url).strip("/")
        self._api = api_prefix.strip("/")
        self._v1 = v1_prefix.strip("/")

    def get_full_endpoint_url(
        self,
        endpoint_url: str,
        resource_prefix: str | None = None,
        query_params: dict[str, str] | None = None,
    ) -> str:
        parts = [self._base, self._api, self._v1]

        if resource_prefix:
            parts.append(resource_prefix.strip("/"))

        if endpoint_url:
            parts.append(endpoint_url.strip("/"))

        url_str = "/".join(p for p in parts if p)

        if query_params:
            url_str = f"{url_str}?{urlencode(query_params)}"

        return url_str
