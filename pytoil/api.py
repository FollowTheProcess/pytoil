"""
Module responsible for querying the GitHub RESTv3 API.

Author: Tom Fleet
Created: 04/02/2021
"""

import json
import urllib.error
import urllib.request
from typing import Dict, List, Optional, Union

# Type hint for generic JSON API response
JSONBlob = Dict[str, Union[List[str], str]]
APIResponse = Union[JSONBlob, List[JSONBlob]]


class API:
    def __init__(self, token: Optional[str] = None) -> None:
        """
        Representation of the GitHub API.

        Args:
            token (Optional[str], optional): GitHub Personal Access Token.
                Defaults to None.
        """
        self.token = token
        self.baseurl: str = "https://api.github.com/"
        self._headers: Dict[str, str] = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}",
        }

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(token={self.token!r})"

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @headers.setter
    def headers(self, value: Dict[str, str]) -> None:
        """
        Incase we ever need to set headers explictly.
        """
        self._headers = value

    # We set no coverage here because this method is almost completely patched out
    # during testing
    def get(self, endpoint: str) -> APIResponse:  # pragma: no cover
        """
        Makes an authenticated request to a GitHub API endpoint
        e.g. 'users/repos'.

        Args:
            endpoint (str): Valid GitHub API endpoint.

        Returns:
            ApiResponse: JSON API response.
        """

        request = urllib.request.Request(
            url=self.baseurl + endpoint, method="GET", headers=self.headers
        )

        with urllib.request.urlopen(request) as r:
            try:
                response: APIResponse = json.loads(r.read())
            except urllib.error.HTTPError:
                raise

        return response
