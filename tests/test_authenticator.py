"""tests for first-use authenticator"""

import pytest
from unittest.mock import Mock

from firstuseauthenticator import FirstUseAuthenticator


@pytest.fixture
def tmpcwd(tmpdir):
    tmpdir.chdir()

# use pytest-asyncio
pytestmark = pytest.mark.asyncio
# run each test in a temporary working directory
pytestmark = pytestmark(pytest.mark.usefixtures("tmpcwd"))


async def test_basic(tmpcwd):
    auth = FirstUseAuthenticator()
    name = "name"
    password = "firstpassword"
    username = await auth.authenticate(Mock(), {"username": name, "password": password})
    assert username == "name"
    # second login, same password
    username = await auth.authenticate(Mock(), {"username": name, "password": password})
    assert username == "name"

    # another login, reusing name but different password
    username = await auth.authenticate(
        Mock(), {"username": name, "password": "differentpassword"}
    )
    assert username is None
