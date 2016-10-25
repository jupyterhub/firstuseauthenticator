"""
JupyterHub Authenticator that lets users set password on first use.

When users first log in, the password they use becomes their
password for that account. It is hashed with bcrypt & stored
locally in a dbm file, and checked next time they log in.
"""
import dbm
from jupyterhub.auth import Authenticator

from tornado import gen
from traitlets.traitlets import Unicode

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

    @gen.coroutine
    def authenticate(self, handler, data):
        # Move everything to bytes
        username = data['username'].encode('utf-8')
        password = data['password'].encode('utf-8')
        with dbm.open(self.dbm_path, 'c', 0o600) as db:
            stored_pw = db.get(username, None)
            if stored_pw is not None:
                if bcrypt.hashpw(password, stored_pw) != stored_pw:
                    return None
            else:
                db[username] = bcrypt.hashpw(password, bcrypt.gensalt())
        return data['username']
