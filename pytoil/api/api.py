"""
Module responsible for handling pytoil's interface with the
GitHub REST v3 API.

Author: Tom Fleet
Created: 19/06/2021
"""


from typing import Any, Dict, List, Optional, Set, Union

import httpx

Response = Dict[str, Any]


class API:
    def __init__(self, username: str, token: str) -> None:
        self.username = username
        self.token = token
        self.baseurl = "https://api.github.com/"
        self.headers: Dict[str, str] = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self.token}",
        }

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"(username={self.username!r}, token={self.token!r})"
        )

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Response:
        """
        Generic authenticated GET request method, used to make a GET
        to any valid GitHub REST v3 API endpoint e.g. 'user/repos'.

        Args:
            endpoint (str): The endpoint to GET.
            params (Optional[Dict[str, Any]], optional): Dictionary of query params to
            pass with the request. Defaults to None.

        Returns:
            Response: JSON Response dict.
        """
        r = httpx.get(url=self.baseurl + endpoint, headers=self.headers, params=params)
        r.raise_for_status()

        response: Response = r.json()

        return response

    def post(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Response:
        """
        Generic authenticated POST request method, used to make a POST
        to any valid GitHub REST v3 API endpoint.

        Args:
            endpoint (str): The endpoint to POST.
            params (Optional[Dict[str, Any]], optional): Dictionary of query params to
            pass with the request. Defaults to None.

        Returns:
            Response: JSON Response dict.
        """

        r = httpx.post(url=self.baseurl + endpoint, headers=self.headers, params=params)
        r.raise_for_status()

        response: Response = r.json()

        return response

    def create_fork(self, owner: str, repo: str) -> Response:
        """
        Create a fork of the specified repository for the authenticated
        user.

        Args:
            owner (str): Owner of the repo to be forked.
            repo (str): Name of the repo to be forked.

        Returns:
            Response: JSON Response dict.
        """

        return self.post(endpoint=f"repos/{owner}/{repo}/forks")

    def get_repo(self, repo: str) -> Response:
        """
        Get a user's repo by name.

        Args:
            repo (str): Name of the repo to get
                (must be owned by the user or will raise a 404)

        Returns:
            Response: JSON Response dict.
        """

        return self.get(endpoint=f"repos/{self.username}/{repo}")

    def get_repos(self) -> Response:
        """
        Gets all repos owned by the authenticated user.

        Returns:
            Response: JSON Response dict.
        """

        return self.get(endpoint="user/repos", params={"type": "owner"})

    def get_repo_names(self) -> Set[str]:
        """
        Gets the names of all the repos owned by the authenticated user.

        Returns:
            Set[str]: Names of all authenticated user repos.
        """

        # For whatever reason, mypy doesn't like this even though it's totally valid
        return {repo["name"] for repo in self.get_repos()}  # type: ignore

    def get_repo_info(self, repo: str) -> Dict[str, Union[str, int]]:
        """
        Returns a dictionary of key information about a particular repo.

        Info Keys:

        - name
        - description
        - created_at
        - updated_at
        - size
        - license

        Args:
            repo (str): Name of the repo to get info for.

        Returns:
            Dict[str, Union[str, int]]: Dict of repo information.
        """

        raw_repo_data = self.get_repo(repo=repo)

        keys_to_get: List[str] = [
            "name",
            "description",
            "created_at",
            "updated_at",
            "size",
            "license",
        ]

        display_dict: Dict[str, Union[str, int]] = {
            key: raw_repo_data.get(key, "Not found") for key in keys_to_get
        }

        # License is itself a dict
        # Couldn't be bothered doing some clever recursive thing for one key
        if raw_repo_data["license"]:
            display_dict["license"] = raw_repo_data.get("license", "Not Found").get(
                "name", "Not Found"
            )

        return display_dict
