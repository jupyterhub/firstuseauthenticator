"""
JupyterHub Authenticator that lets users set password on first use.

When users first log in, the password they use becomes their
password for that account. It is hashed with bcrypt & stored
locally in a dbm file, and checked next time they log in.
"""
import dbm
from jupyterhub.auth import Authenticator
from jupyterhub.orm import User

from tornado import gen
from traitlets.traitlets import Unicode, Bool

import bcrypt


class FirstUseAuthenticator(Authenticator):
    """
    JupyterHub authenticator that lets users set password on first use.
    """
    dbm_path = Unicode(
        'passwords.dbm',
        config=True,
        help="""
        Path to store the db file with username / pwd hash in
        """
    )

    create_users = Bool(
        True,
        config=True,
        help="""
        Create users if they do not exist already.

        When set to false, users would have to be explicitly created before
        they can log in. Users can be created via the admin panel or by setting
        whitelist / admin list.
        """
    )

    def _user_exists(self, username):
        """
        Return true if given user already exists.

        Note: Depends on internal details of JupyterHub that might change
        across versions. Tested with v0.9
        """
        return self.db.query(User).filter_by(name=username).first() is not None

    @gen.coroutine
    def authenticate(self, handler, data):
        username = data['username']

        if not self.create_users:
            if not self._user_exists(username):
                return None

        password = data['password']
        with dbm.open(self.dbm_path, 'c', 0o600) as db:
            stored_pw = db.get(username.encode(), None)
            if stored_pw is not None:
                if bcrypt.hashpw(password.encode(), stored_pw) != stored_pw:
                    return None
            else:
                db[username] = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return username

    def delete_user(self, user):
        """
        When user is deleted, remove their entry from password db.

        This lets passwords be reset by deleting users.
        """
        with dbm.open(self.dbm_path, 'c', 0o600) as db:
            del db[user.name]
