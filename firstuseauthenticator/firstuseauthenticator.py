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
from jupyterhub.handlers import LoginHandler
from jupyterhub.orm import User

from tornado import gen, web
from traitlets.traitlets import Unicode, Bool, Integer

import bcrypt


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class CustomLoginHandler(LoginHandler):
    """
    Render the login page.

    Allows customising the login error when more specific
    feedback is needed. Checkout
    https://github.com/jupyterhub/firstuseauthenticator/pull/21#discussion_r364252009
    for more details
    """
    custom_login_error = 'Invalid username or password'
    def _render(self, login_error=None, username=None):
        return super()._render(self.custom_login_error, username)


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
        user = self.current_user
        new_password = self.get_body_argument('password', strip=False)
        msg = self.authenticator.reset_password(user.name, new_password)

        if "success" in msg:
            alert = "success"
        else:
            alert = "danger"

        html = self.render_template(
            'reset.html',
            result=True,
            alert=alert,
            result_message=msg,
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

    min_password_length = Integer(
        7,
        config=True,
        help="""
        The minimum length of the password when user is created.
        When set to 0, users will be allowed to set 0 length passwords.
        """
    )

    def _user_exists(self, username):
        """
        Return true if given user already exists.

        Note: Depends on internal details of JupyterHub that might change
        across versions. Tested with v0.9
        """
        return self.db.query(User).filter_by(name=username).first() is not None


    def _validate_password(self, password):
        return len(password) >= self.min_password_length


    def validate_username(self, name):
        invalid_chars = [',', ' ']
        if any((char in name) for char in invalid_chars):
            return False
        return super().validate_username(name)

    @gen.coroutine
    def authenticate(self, handler, data):
        username = data['username']

        if not self.create_users:
            if not self._user_exists(username):
                return None

        password = data['password']
        # Don't enforce password length requirement on existing users, since that can
        # lock users out of their hubs.
        if not self._validate_password(password) and not self._user_exists(username):
            handler.custom_login_error = (
                'Password too short! Please choose a password at least %d characters long.'
                % self.min_password_length
            )

            self.log.error(handler.custom_login_error)
            return None
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
        try:
            with dbm.open(self.dbm_path, 'c', 0o600) as db:
                del db[user.name]
        except KeyError as k:
            pass

    def reset_password(self, username, new_password):
        """
        This allows changing the password of a logged user.
        """
        if not self._validate_password(new_password):
            login_err = (
                'Password too short! Please choose a password at least %d characters long.'
                % self.min_password_length
            )
            self.log.error(login_err)
            # Resetting the password will fail if the new password is too short.
            return login_err
        with dbm.open(self.dbm_path, 'c', 0o600) as db:
            db[username] = bcrypt.hashpw(new_password.encode(),
                                         bcrypt.gensalt())
        login_msg = "Your password has been changed successfully!"
        self.log.info(login_msg)
        return login_msg

    def get_handlers(self, app):
        return [(r'/login', CustomLoginHandler), (r'/auth/change-password',ResetPasswordHandler)]
