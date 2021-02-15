"""
Tests for the API module.

Author: Tom Fleet
Created: 05/02/2021
"""


from typing import NamedTuple

import pytest

import pytoil
from pytoil.api import API
from pytoil.exceptions import APIRequestError


def test_api_init_passed():

    api = API(token="definitelynotatoken", username="me")

    assert api.token == "definitelynotatoken"
    assert api.username == "me"
    assert api.baseurl == "https://api.github.com/"
    assert api.headers == {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token definitelynotatoken",
    }


def test_api_init_default(mocker, temp_config_file):

    # Patch out the default CONFIG_PATH for our temp file
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        api = API()

        assert api.token == "tempfiletoken"
        assert api.username == "tempfileuser"
        assert api.baseurl == "https://api.github.com/"
        assert api.headers == {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "token tempfiletoken",
        }


def test_api_repr_passed():

    api = API(token="definitelynotatoken", username="me")

    assert api.__repr__() == "API(token='definitelynotatoken', username='me')"


def test_api_repr_default(mocker, temp_config_file):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        api = API()

        assert api.__repr__() == "API(token='tempfiletoken', username='tempfileuser')"


def test_api_setters():

    api = API(token="definitelynotatoken", username="me")

    # Assert properties before
    assert api.headers == {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token definitelynotatoken",
    }
    assert api.token == "definitelynotatoken"
    assert api.username == "me"

    # Change properties
    api.headers = {"dingle": "dongle", "dangle": "dungle"}
    api.token = "anotherfaketoken"
    api.username = "someoneelse"

    # Assert after
    assert api.headers == {"dingle": "dongle", "dangle": "dungle"}
    assert api.token == "anotherfaketoken"
    assert api.username == "someoneelse"


@pytest.mark.parametrize("status_code", [300, 302, 404, 400, 401, 408, 502, 500])
def test_get_raises_on_invalid_request(mocker, status_code, temp_config_file):

    # Patch the default config file location to our temp file
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        class FakeResponseObject(NamedTuple):
            """
            Fake HTTP response so our mock request has a response
            with a `.status` attribute.
            """

            status: int = status_code

        api = API(token="notatoken", username="hello")

        mocker.patch(
            "pytoil.api.urllib3.PoolManager.request",
            autospec=True,
            return_value=FakeResponseObject(),
        )

        with pytest.raises(APIRequestError) as err:
            api.get("not/here")
            assert err.status_code == status_code


def test_get_doesnt_raise_on_valid_request(mocker, temp_config_file):

    # Patch the default config file location to our temp file
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        class FakeResponseData(NamedTuple):
            """
            Fake response data class with a decode method so
            that `r.data.decode` works as expected.
            """

            data: str = '{"fake": "json"}'

            def decode(self, encoding: str = "utf-8"):
                return self.data

        class FakeResponseObject:
            """
            Fake HTTP response so our mock request has a response
            with a `.status` attribute.
            """

            def __init__(
                self, data: FakeResponseData = FakeResponseData(), status: int = 200
            ):
                self.data = data
                self.status = status

        api = API(token="notatoken", username="hello")

        mocker.patch(
            "pytoil.api.urllib3.PoolManager.request",
            autospec=True,
            return_value=FakeResponseObject(),
        )

        # If this raises, the test fails
        resp = api.get("fake/endpoint")

        assert resp == {"fake": "json"}


def test_get_user_repo_correctly_calls_get(mocker, fake_api_response):

    mocker.patch("pytoil.api.API.get", autospec=True, return_value=fake_api_response)

    api = API(token="definitelynotatoken", username="me")

    assert api.get_repo(repo="fakey") == fake_api_response


def test_get_user_repos_correctly_calls_get(mocker, fake_api_response):

    mocker.patch("pytoil.api.API.get", autospec=True, return_value=fake_api_response)

    api = API(token="definitelynotatoken", username="me")

    assert api.get_repos() == fake_api_response


@pytest.mark.parametrize(
    "status_code", [204, 206, 300, 302, 404, 400, 401, 408, 502, 500]
)
def test_post_raises_on_invalid_request(mocker, status_code, temp_config_file):

    # Patch the default config file location to our temp file
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        class FakeResponseObject(NamedTuple):
            """
            Fake HTTP response so our mock request has a response
            with a `.status` attribute.
            """

            status: int = status_code

        api = API(token="notatoken", username="hello")

        mocker.patch(
            "pytoil.api.urllib3.PoolManager.request",
            autospec=True,
            return_value=FakeResponseObject(),
        )

        with pytest.raises(APIRequestError) as err:
            api.post("not/here")
            assert err.status_code == status_code


def test_post_doesnt_raise_on_valid_request(mocker, temp_config_file):

    # Patch the default config file location to our temp file
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        class FakeResponseData(NamedTuple):
            """
            Fake response data class with a decode method so
            that `r.data.decode` works as expected.
            """

            data: str = '{"fake": "json"}'

            def decode(self, encoding: str = "utf-8"):
                return self.data

        class FakeResponseObject:
            """
            Fake HTTP response so our mock request has a response
            with a `.status` attribute.
            """

            def __init__(
                self, data: FakeResponseData = FakeResponseData(), status: int = 200
            ):
                self.data = data
                self.status = status

        api = API(token="notatoken", username="hello")

        mocker.patch(
            "pytoil.api.urllib3.PoolManager.request",
            autospec=True,
            return_value=FakeResponseObject(),
        )

        # If this raises, the test fails
        resp = api.post("fake/endpoint")

        assert resp == {"fake": "json"}


def test_fork_repo_raises_if_owner_matches_username(mocker, temp_config_file):

    # Patch the default config file location to our temp file
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        api = API(token="notatoken", username="hello")

        with pytest.raises(APIRequestError):
            api.fork_repo(owner="hello", name="project")


def test_fork_repo_returns_if_owner_doesnt_match_username(mocker, temp_config_file):

    # Patch the default config file location to our temp file
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Patch out api.post to return some arbitrary json
        # and more importantly, not actually hit the GitHub API
        mocker.patch(
            "pytoil.api.API.post",
            autospec=True,
            return_value={"arbitrary": "json", "blob": "yes"},
        )

        api = API(token="notatoken", username="hello")

        # Fork a repo with a different user name
        response = api.fork_repo(owner="someoneelse", name="project")

        assert response == {"arbitrary": "json", "blob": "yes"}
