"""tests for first-use authenticator"""

import pytest
import logging
from unittest import mock

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
    username = await auth.authenticate(mock.Mock(), {"username": name, "password": password})
    assert username == "name"
    # second login, same password
    username = await auth.authenticate(mock.Mock(), {"username": name, "password": password})
    assert username == "name"

    # another login, reusing name but different password
    username = await auth.authenticate(
        mock.Mock(), {"username": name, "password": "differentpassword"}
    )
    assert username is None

async def test_min_pass_lenght(caplog, tmpcwd):
    users = []
    def user_exists(username):
        return username in users

    auth = FirstUseAuthenticator()

    # allow passwords with any lenght
    auth.min_password_lenght = 0

    # new user, first login, any password allowed
    name = "name"
    password = ""
    with mock.patch.object(auth, '_user_exists', user_exists):
        username = await auth.authenticate(mock.Mock(), {"username": name, "password": password})
        assert username == "name"
        users.append(name)

    # reject passwords that are less than 10 characters in lenght
    auth.min_password_lenght = 10

    # existing user, second login, only passwords longer than 10 chars allowed
    with mock.patch.object(auth, '_user_exists', user_exists):
        username = await auth.authenticate(mock.Mock(), {"username": name, "password": password})
        # assert existing users are not impacted by the new lenght rule
        for record in caplog.records:
            assert record.levelname != 'ERROR'

    # new user, first login, only passwords longer than 10 chars allowed
    name = "newuser"
    password = "tooshort"
    with mock.patch.object(auth, '_user_exists', user_exists):
        username = await auth.authenticate(mock.Mock(), {"username": name, "password": password})
        assert username is None
        # assert that new users' passwords must have the specified lenght
        for record in caplog.records:
            if record.levelname == 'ERROR':
                assert record.msg == f'Password too short! \
                Please choose a password at least {auth.min_password_lenght} characters long.'
