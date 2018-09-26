"""
JupyterHub Authenticator that lets users set password on first use.

When users first log in, the password they use becomes their
password for that account. It is hashed with bcrypt & stored
locally in a dbm file, and checked next time they log in.
"""
import dbm
import os
from jinja2 import ChoiceLoader, FileSystemLoader
from jupyterhub.auth import Authenticator
from jupyterhub.handlers import BaseHandler
from jupyterhub.orm import User

from tornado import gen, web
from traitlets.traitlets import Unicode, Bool

import bcrypt


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class ResetPasswordHandler(BaseHandler):
    """Render the reset password page."""
    def __init__(self, *args, **kwargs):
        self._loaded = False
        super().__init__(*args, **kwargs)

    def _register_template_path(self):
        if self._loaded:
            return

        self.log.debug('Adding %s to template path', TEMPLATE_DIR)
        loader = FileSystemLoader([TEMPLATE_DIR])

        env = self.settings['jinja2_env']
        previous_loader = env.loader
        env.loader = ChoiceLoader([previous_loader, loader])

        self._loaded = True

    @web.authenticated
    async def get(self):
        self._register_template_path()
        html = self.render_template('reset.html')
        self.finish(html)

    @web.authenticated
    async def post(self):
        user = self.get_current_user()
        new_password = self.get_body_argument('password', strip=False)
        self.authenticator.reset_password(user.name, new_password)

        html = self.render_template(
            'reset.html',
            result=True,
            result_message='your password has been changed successfully',
        )
        self.finish(html)


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
                db[username] = bcrypt.hashpw(password.encode(),
                                             bcrypt.gensalt())
        return username

    def delete_user(self, user):
        """
        When user is deleted, remove their entry from password db.

        This lets passwords be reset by deleting users.
        """
        with dbm.open(self.dbm_path, 'c', 0o600) as db:
            del db[user.name]

    def reset_password(self, username, new_password):
        """
        This allow to change password of a logged user.
        """
        with dbm.open(self.dbm_path, 'c', 0o600) as db:
            db[username] = bcrypt.hashpw(new_password.encode(),
                                         bcrypt.gensalt())
        return username

    def get_handlers(self, app):
        return super().get_handlers(app) + [(r'/auth/change-password',
                                            ResetPasswordHandler)]
