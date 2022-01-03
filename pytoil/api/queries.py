"""
GraphQL queries needed for pytoil's API calls.


Author: Tom Fleet
Created: 21/12/2021
"""

GET_REPO_NAMES = """
query ($username: String!, $limit: Int!) {
  user(login: $username) {
    repositories(first: $limit, ownerAffiliations: OWNER, orderBy: {field: NAME, direction: ASC}) {
      nodes {
        name
      }
    }
  }
}
"""

GET_FORK_NAMES = """
query ($username: String!, $limit: Int!) {
  user(login: $username) {
    repositories(first: $limit, ownerAffiliations: OWNER, isFork: true, orderBy: {field: NAME, direction: ASC}) {
      nodes {
        name
      }
    }
  }
}
"""

CHECK_REPO_EXISTS = """
query ($username: String!, $name: String!) {
  repository(owner: $username, name: $name) {
    name
  }
}
"""


GET_REPO_INFO = """
query ($username: String!, $name: String!) {
  repository(owner: $username, name: $name) {
    name,
    description,
    createdAt,
    updatedAt,
    diskUsage,
    licenseInfo {
      name
    }
  }
}
"""