"""
Pydantic models of the GitHub REST v3 API responses used in pytoil.

These models provide both editor completions type checking and validation.


Author: Tom Fleet
Created: 01/09/2021
"""


from __future__ import annotations

import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class Owner(BaseModel):
    """
    Model representing a GitHub repository Owner.
    """

    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: Optional[str]
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool


class License(BaseModel):
    """
    Model representing a GitHub known Open Source License.
    """

    key: str
    name: str
    spdx_id: str
    url: str
    node_id: str


class Repository(BaseModel):
    """
    Model representing a single GitHub Repository as returned from
    the GET /repos/{owner}/{repo} endpoint.
    """

    id: int
    node_id: str
    name: str
    full_name: str
    owner: Owner
    private: bool
    html_url: str
    description: str
    fork: bool
    url: str
    archive_url: str
    assignees_url: str
    blobs_url: str
    branches_url: str
    collaborators_url: str
    comments_url: str
    commits_url: str
    compare_url: str
    contents_url: str
    contributors_url: str
    deployments_url: str
    downloads_url: str
    events_url: str
    forks_url: str
    git_commits_url: str
    git_refs_url: str
    git_tags_url: str
    git_url: str
    issue_comment_url: str
    issue_events_url: str
    issues_url: str
    keys_url: str
    labels_url: str
    languages_url: str
    merges_url: str
    milestones_url: str
    notifications_url: str
    pulls_url: str
    releases_url: str
    ssh_url: str
    stargazers_url: str
    statuses_url: str
    subscribers_url: str
    subscriptions_url: Optional[str]
    tags_url: str
    teams_url: str
    trees_url: str
    clone_url: str
    mirror_url: Optional[str]
    hooks_url: str
    svn_url: str
    homepage: Optional[str]
    language: Optional[str]
    forks_count: int
    forks: int
    stargazers_count: int
    watcher_count: Optional[int]
    watchers: int
    size: int
    default_branch: str
    open_issues_count: int
    open_issues: int
    is_template: Optional[bool]
    topics: Optional[List[str]]
    has_issues: bool
    has_projects: bool
    has_wiki: bool
    has_pages: bool
    has_downloads: bool
    archived: bool
    disabled: bool
    visibility: Optional[str]
    pushed_at: datetime.datetime
    created_at: datetime.datetime
    updated_at: datetime.datetime
    permissions: Dict[str, bool]
    allow_rebase_merge: Optional[bool]
    temp_clone_token: Optional[str]
    allow_squash_merge: Optional[bool]
    allow_auto_merge: Optional[bool]
    delete_branch_on_merge: Optional[bool]
    allow_merge_commit: Optional[bool]
    subscribers_count: Optional[int]
    network_count: Optional[int]
    template_repository: Optional[Repository]
    license: Optional[License]
    organization: Optional[Owner]
    parent: Optional[Repository]
    source: Optional[Repository]


class RepoSummaryInfo(BaseModel):
    """
    RepoSummaryInfo is the internal pytoil model used
    to display basic info to the user about a repo.
    """

    name: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    size: int
    license: Optional[str]


class RepoList(BaseModel):
    """
    RepoList is the model responsible for handling multiple
    Repositories e.g. from the response from 'user/repos'
    """

    repos: List[Repository]


# This ensures that recursive model definitions work as expected
# see https://pydantic-docs.helpmanual.io/usage/models/#recursive-models
Repository.update_forward_refs()
