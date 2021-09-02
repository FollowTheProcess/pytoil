"""
Module responsible for handling pytoil's interface with the
GitHub REST v3 API.

Author: Tom Fleet
Created: 19/06/2021
"""


from typing import Any, Dict, List, Optional, Set, Union

import httpx

from pytoil.api.models import Repository, RepoSummaryInfo


class API:
    """
    The GitHub API class.
    """

    def __init__(self, username: str, token: str) -> None:
        """
        A container with useful attributes and methods for
        hitting the GitHub REST API.

        Args:
            username (str): The user's GitHub username.
            token (str): The user's GitHub OAUTH token (personal access token)
        """
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

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Generic authenticated GET request method, used to make a GET
        to any valid GitHub REST v3 API endpoint e.g. 'user/repos'.

        Args:
            endpoint (str): The endpoint to GET.
            params (Optional[Dict[str, Any]], optional): Dictionary of query params to
            pass with the request. Defaults to None.

        Returns:
            Dict[str, Any]: JSON Response dict.
        """
        r = httpx.get(url=self.baseurl + endpoint, headers=self.headers, params=params)
        r.raise_for_status()
        resp: Dict[str, Any] = r.json()

        return resp

    def post(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generic authenticated POST request method, used to make a POST
        to any valid GitHub REST v3 API endpoint.

        Args:
            endpoint (str): The endpoint to POST.
            params (Optional[Dict[str, Any]], optional): Dictionary of query params to
            pass with the request. Defaults to None.

        Returns:
            Dict[str, Any]: JSON Response dict.
        """

        r = httpx.post(url=self.baseurl + endpoint, headers=self.headers, params=params)
        r.raise_for_status()
        resp: Dict[str, Any] = r.json()

        return resp

    def create_fork(self, owner: str, repo: str) -> Repository:
        """
        Create a fork of the specified repository for the authenticated
        user.

        Args:
            owner (str): Owner of the repo to be forked.
            repo (str): Name of the repo to be forked.

        Returns:
            Repository: The GitHub Repository model for the new fork.
        """
        response = self.post(endpoint=f"repos/{owner}/{repo}/forks")
        return Repository(**response)

    def get_forks(self) -> List[Repository]:
        """
        Gets all the repos that are forks.

        Returns:
            List[Repository]: List of GitHub Repositories belonging
                to the authenticated user that are forks.
        """
        repos = self.get_repos()
        return [repo for repo in repos if repo.fork]

    def get_fork_names(self) -> List[str]:
        """
        Gets the names of all the user's repos that are forks
        of other repos.

        Returns:
            List[str]: Names of all the forked repos.
        """
        forks = self.get_forks()
        return [fork.name for fork in forks]

    def get_repo(self, repo: str) -> Repository:
        """
        Get a user's repo by name.

        Args:
            repo (str): Name of the repo to get
                (must be owned by the user or will raise a 404)

        Returns:
            Repository: The GitHub Repository response model for the repo.
        """
        response = self.get(endpoint=f"repos/{self.username}/{repo}")
        return Repository(**response)  # type: ignore

    def get_repos(self) -> List[Repository]:
        """
        Gets all repos owned by the authenticated user.

        Returns:
            List[Repository]: List of GitHub Repository objects belonging
                to the authenticated user.
        """
        response = self.get(endpoint="user/repos", params={"type": "owner"})
        return [Repository(**item) for item in response]  # type: ignore

    def get_repo_names(self) -> Set[str]:
        """
        Gets the names of all the repos owned by the authenticated user.

        Returns:
            Set[str]: Names of all authenticated user repos.
        """
        return {repo.name for repo in self.get_repos()}

    def get_repo_info(self, repo: str) -> RepoSummaryInfo:
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
            RepoSummaryInfo:
        """
        repository = self.get_repo(repo)

        info_dict = {
            "name": repository.name,
            "description": repository.description,
            "created_at": repository.created_at,
            "updated_at": repository.updated_at,
            "size": repository.size,
            "license": repository.license.name if repository.license else None,
        }

        return RepoSummaryInfo(**info_dict)
