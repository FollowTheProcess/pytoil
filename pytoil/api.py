"""
Module responsible for querying the GitHub RESTv3 API.

Author: Tom Fleet
Created: 04/02/2021
"""

import json
from typing import Any, Dict, List, Optional, Union

import urllib3

from .config import Config
from .exceptions import APIRequestError

# Type hint for generic JSON API response
# either a single JSON blob or a list of JSON blobs
RepoBlob = Dict[str, Any]
APIResponse = List[RepoBlob]


class API:
    def __init__(
        self, token: Optional[str] = None, username: Optional[str] = None
    ) -> None:
        """
        Representation of the GitHub API.

        Args:
            token (Optional[str], optional): GitHub Personal Access Token.
                Defaults to value from config file.

            username (Optional[str], optional): Users GitHub username.
                Defaults to value from config file.
        """
        # If token passed, set it
        # if not, get from config
        self._token = token or Config.get().token
        # If username passed, set it
        # if not, get from config
        self._username = username or Config.get().username

        self.baseurl: str = "https://api.github.com/"

        self._headers: Dict[str, str] = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self._token}",
        }
        self.http = urllib3.PoolManager()

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"(token={self._token!r}, "
            + f"username={self.username!r})"
        )

    @property
    def token(self) -> Union[str, None]:
        return self._token

    @token.setter
    def token(self, value: str) -> None:
        self._token = value

    @property
    def username(self) -> Union[str, None]:
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        self._username = value

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @headers.setter
    def headers(self, value: Dict[str, str]) -> None:
        """
        Incase we ever need to set headers explictly.
        """
        self._headers = value

    def get(self, endpoint: str) -> APIResponse:
        """
        Makes an authenticated request to a GitHub API endpoint
        e.g. 'users/repos'.

        Generic base for more specific get methods below.

        Args:
            endpoint (str): Valid GitHub API endpoint.

        Raises:
            APIRequestError: If any HTTP error occurs, will raise an exception
                and give a description and standard HTTP status code.

        Returns:
            ApiResponse: JSON API response.
        """
        # Validate the config
        Config.get().raise_if_unset()

        r = self.http.request(
            method="GET", url=self.baseurl + endpoint, headers=self.headers
        )
        if r.status != 200:
            raise APIRequestError(
                f"""GitHub API endpoint: {endpoint} gave HTTP Response: {r.status}.
                Method: GET""",
                status_code=r.status,
            )
        else:
            response: APIResponse = json.loads(r.data.decode("utf-8"))

        return response

    def post(self, endpoint: str) -> APIResponse:
        """
        Makes an authenticated POST request to a GitHub API
        endpoint e.g. '/repos/{owner}/{repo}/forks'.

        Generic base for more specific post methods below.

        Args:
            endpoint (str): Valid GitHub API endpoint.

        Raises:
            APIRequestError: If any HTTP error occurs, will raise an exception
                and give a description and standard HTTP status code.

        Returns:
            APIResponse: JSON API response.
        """

        # Validate the config
        Config.get().raise_if_unset()

        r = self.http.request(
            method="POST", url=self.baseurl + endpoint, headers=self.headers
        )

        # POSTs could return 202's
        if r.status > 202:
            raise APIRequestError(
                f"""GitHub API endpoint: {endpoint} gave HTTP Response: {r.status}.
                Method: POST.""",
                status_code=r.status,
            )

        else:
            response: APIResponse = json.loads(r.data.decode("utf-8"))

        return response

    def get_repo(self, repo: str) -> APIResponse:
        """
        Hits the GitHub REST API 'repos/{owner}/repo' endpoint
        and parses the response.

        In other words it gets the JSON representing a particular `repo`
        belonging to {owner}. In our case, {owner} is `self.username`.

        Args:
            repo (str): The name of the repo to fetch JSON for.

        Raises:
            MissingUsernameError: If `self.username` is None indicating it has
                not been set in the ~/.pytoil.yml config file.

        Returns:
            APIResponse: JSON response for a particular repo.
        """

        return self.get(f"repos/{self.username}/{repo}")

    def get_repos(self) -> APIResponse:
        """
        Hits the GitHub REST API 'user/{username}/repos' endpoint and parses
        the response.

        Function similar to `get_repo` the difference being `get_repos` returns
        a list of JSON blobs each representing a repo belonging to `self.username`

        This endpoint requires no parameters because it is the
        'get repos for authenticated user' endpoint and since at this point we have
        `self.token` this automatically fills in the {username} for us.

        Returns:
            APIResponse: JSON response for a list of all users repos.
        """

        # Because the user is authenticated (token)
        # This gets their repos
        # get will raise if missing token
        return self.get("user/repos")

    def get_repo_names(self) -> List[str]:
        """
        Hits the GitHub REST API 'user/{username}/repos' endpoint, parses
        the response, extracts the name of each repo and returns
        a list of these names.

        Returns:
            List[str]: List of user's repo names.
        """

        raw_repo_data = self.get_repos()

        names = [repo["name"] for repo in raw_repo_data]

        return names

    def fork_repo(self, owner: str, name: str) -> APIResponse:
        """
        Fork a repo called `name` owned by `owner` to the users
        GitHub repos.

        Don't have to specify the user because this is an authenticated
        only request, user identification is provided by the `token`
        in `self.headers`.

        Args:
            owner (str): Owner of the repo to be forked.
            name (str): Name of the repo to be forked.

        Raises:
            APIRequestError: If any HTTP error occurs.

        Returns:
            APIResponse: JSON API response.
        """

        # Validate the config
        Config.get().raise_if_unset()

        # Can't fork your own repo
        if self.username == owner:
            raise APIRequestError(
                f"""Forking of repo: {owner}/{name} invalid.
            Cannot fork a repo that you already own.""",
                status_code=400,
            )
        else:
            return self.post(f"repos/{owner}/{name}/forks")
