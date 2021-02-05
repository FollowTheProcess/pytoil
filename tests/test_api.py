"""
Tests for the API module.

Author: Tom Fleet
Created: 05/02/2021
"""

import urllib.error

import pytest

from pytoil.api import API


def test_api_init():

    api = API(token="definitelynotatoken")

    assert api.token == "definitelynotatoken"
    assert api.baseurl == "https://api.github.com/"
    assert api.headers == {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token definitelynotatoken",
    }


def test_api_repr():

    api = API(token="definitelynotatoken")

    assert api.__repr__() == "API(token='definitelynotatoken')"


def test_api_headers_setter():

    api = API(token="definitelynotatoken")

    # Assert headers before
    assert api.headers == {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token definitelynotatoken",
    }

    # Change headers
    api.headers = {"dingle": "dongle", "dangle": "dungle"}

    # Assert headers after
    assert api.headers == {"dingle": "dongle", "dangle": "dungle"}


def test_get_raises_on_invalid_request(mocker):

    api = API(token="definitelynotatoken")

    mocker.patch(
        "pytoil.api.urllib.request.urlopen",
        autospec=True,
        side_effect=urllib.error.HTTPError(
            "https://api.github.com/not/here",
            404,
            "Not Found",
            api.headers,
            None,
        ),
    )

    with pytest.raises(urllib.error.HTTPError):
        api.get("not/here")
