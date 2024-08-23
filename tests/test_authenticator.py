"""tests for first-use authenticator"""

from unittest import mock

import dbm
import pytest

from firstuseauthenticator import FirstUseAuthenticator


@pytest.fixture(autouse=True)
def tmpcwd(tmpdir):
    tmpdir.chdir()


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

async def test_min_pass_length(caplog, tmpcwd):
    users = []
    def user_exists(username):
        return username in users

    auth = FirstUseAuthenticator()

    # allow passwords with any length
    auth.min_password_length = 0

    # new user, first login, any password allowed
    name = "name"
    password = ""
    with mock.patch.object(auth, '_user_exists', user_exists):
        username = await auth.authenticate(mock.Mock(), {"username": name, "password": password})
        assert username == "name"
        users.append(name)

    # reject passwords that are less than 10 characters in length
    auth.min_password_length = 10

    # existing user, second login, only passwords longer than 10 chars allowed
    with mock.patch.object(auth, '_user_exists', user_exists):
        username = await auth.authenticate(mock.Mock(), {"username": name, "password": password})
        # assert existing users are not impacted by the new length rule
        for record in caplog.records:
            assert record.levelname != 'ERROR'

    # new user, first login, only passwords longer than 10 chars allowed
    name = "newuser"
    password = "tooshort"
    with mock.patch.object(auth, '_user_exists', user_exists):
        username = await auth.authenticate(mock.Mock(), {"username": name, "password": password})
        assert username is None
        # assert that new users' passwords must have the specified length
        for record in caplog.records:
            if record.levelname == 'ERROR':
                assert record.msg == (
                    'Password too short! Please choose a password at least %d characters long.'
                    % auth.min_password_length
                )


async def test_normalized_check(caplog, tmpcwd):
    # cases:
    # 1.a - normalized
    # 1.b not normalized, no collision
    # 2.a normalized present, collision
    # 2.b normalized not present, collision
    # disable normalization, populate db with duplicates
    to_load = [
        "onlynormalized",
        "onlyNotNormalized",
        "collisionnormalized",
        "collisionNormalized",
        "collisionNotNormalized",
        "collisionNotnormalized",
    ]

    # load passwords
    auth1 = FirstUseAuthenticator()
    with mock.patch.object(auth1, "normalize_username", lambda x: x):
        for username in to_load:
            assert await auth1.authenticate(
                mock.Mock(),
                {
                    "username": username,
                    "password": username,
                },
            )

    # first make sure normalization was skipped
    with dbm.open(auth1.dbm_path) as db:
        for username in to_load:
            assert db.get(username.encode("utf8"))
    # at startup, normalization is checked
    auth2 = FirstUseAuthenticator()
    with dbm.open(auth1.dbm_path) as db:
        passwords = {key.decode("utf8"): db[key].decode("utf8") for key in db.keys()}
    in_db = set(passwords)
    # 1.a no-op
    assert "onlynormalized" in in_db
    # 1.b renamed
    assert "onlynotnormalized" in in_db
    assert "onlyNotNormalized" not in in_db
    # 2.a collision, preserve normalized
    assert "collisionnormalized" in in_db
    assert "collisionNormalized" not in in_db
    # 2.b collision, preserve and add normalized
    assert "collisionnotnormalized" in in_db
    assert "collisionNotNormalized" not in in_db
    assert "collisionNotnormalized" not in in_db

    # check the backup
    with dbm.open(auth1.dbm_path + "-backup") as db:
        backup_passwords = {
            key.decode("utf8"): db[key].decode("utf8") for key in db.keys()
        }

    for name in to_load:
        assert name in backup_passwords

    # now verify logins
    m = mock.Mock()
    for username, password in (
        ("onlynormalized", "onlynormalized"),
        ("onlyNormalized", "onlynormalized"),
        ("onlynotnormalized", "onlyNotNormalized"),
        ("onlyNotNormalized", "onlyNotNormalized"),
        ("collisionnormalized", "collisionnormalized"),
        ("collisionNormalized", "collisionnormalized"),
        ("collisionnotnormalized", "collisionNotNormalized"),
        ("collisionNotNormalized", "collisionNotNormalized"),
    ):
        # normalized form, doesn't reset password
        authenticated = await auth2.authenticate(
            m,
            {
                "username": username,
                "password": "firstuse",
            },
        )
        assert authenticated is None

        # non-normalized form, doesn't reset password
        authenticated = await auth2.authenticate(
            m,
            {
                "username": username.upper(),
                "password": "firstuse",
            },
        )
        assert authenticated is None

        # normalized form, accepts correct password
        authenticated = await auth2.authenticate(
            m,
            {
                "username": username,
                "password": password,
            },
        )
        assert authenticated
        assert authenticated == auth2.normalize_username(username)

        # non-normalized form, accepts correct password
        authenticated = await auth2.authenticate(
            m,
            {
                "username": username.upper(),
                "password": password,
            },
        )
        assert authenticated
        assert authenticated == auth2.normalize_username(username)

    # load again, should skip the
    auth3 = FirstUseAuthenticator()
