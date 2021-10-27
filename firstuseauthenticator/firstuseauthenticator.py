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

from tornado import web
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
    custom_login_error = ''

    def _render(self, login_error=None, username=None):
        if self.custom_login_error:
            login_error = self.custom_login_error
        return super()._render(login_error, username)


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
        html = await self.render_template('reset.html')
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

        html = await self.render_template(
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

    check_passwords_on_startup = Bool(
        True,
        config=True,
        help="""
        Check for non-normalized-username passwords on startup.
        """,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.check_passwords_on_startup:
            self._check_passwords()

    def _check_passwords(self):
        """Validation checks on the password database at startup

        Mainly checks for the presence of passwords for non-normalized usernames

        If a username is present only in one non-normalized form,
        it will be renamed to the normalized form.

        If multiple forms of the same normalized username are present,
        ensure that at least the normalized form is also present.
        It will continue to produce warnings until manual intervention removes the non-normalized entries.

        Non-normalized entries will never be used during login.
        """
        with dbm.open(self.dbm_path, "c", 0o600) as db:
            # load the username:hashed_password dict
            passwords = {}
            for key in db.keys():
                passwords[key.decode("utf8")] = db[key]

            # normalization map
            # compute the full map before checking in case two non-normalized forms are used
            # keys are normalized usernames,
            # values are lists of all names present in the db
            # which normalize to the same user
            normalized_usernames = {}
            for username in passwords:
                normalized_username = self.normalize_username(username)
                normalized_usernames.setdefault(normalized_username, []).append(
                    username
                )

            # check if any non-normalized usernames are in the db
            for normalized_username, usernames in normalized_usernames.items():
                # case 1. only one form, make sure it's stored in the normalized username
                if len(usernames) == 1:
                    username = usernames[0]
                    # case 1.a only normalized form, nothing to do
                    if username == normalized_username:
                        continue
                    # 1.b only one form, not normalized. Unambiguous to fix.
                    # move password from non-normalized to normalized.
                    self.log.warning(
                        f"Normalizing username in password db {username}->{normalized_username}"
                    )
                    db[normalized_username.encode("utf8")] = passwords[username]
                    del db[username]
                else:
                    # collision! Multiple passwords for the same Hub user with different normalization
                    # do not clear these automatically because the 'right' answer is ambiguous,
                    # but make sure the normalized_username is set,
                    # so that after upgrade, there is always a password set
                    # the non-normalized username passwords will never be used
                    # after jupyterhub-firstuseauthenticator 1.0
                    self.log.warning(
                        f"{len(usernames)} forms of {normalized_username} present in password db: {usernames}. Only {normalized_username} will be used."
                    )
                    if normalized_username not in passwords:
                        username = usernames[0]
                        self.log.warning(
                            f"Normalizing username in password db {username}->{normalized_username}"
                        )
                        db[normalized_username.encode("utf8")] = passwords[username]

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

    async def authenticate(self, handler, data):
        username = self.normalize_username(data['username'])
        password = data['password']

        if not self.create_users:
            if not self._user_exists(username):
                return None

        with dbm.open(self.dbm_path, 'c', 0o600) as db:
            stored_pw = db.get(username.encode("utf8"), None)

            if stored_pw is not None:
                # for existing passwords: ensure password hash match
                if bcrypt.hashpw(password.encode("utf8"), stored_pw) != stored_pw:
                    return None
            else:
                # for new users: ensure password validity and store password hash
                if not self._validate_password(password):
                    handler.custom_login_error = (
                        'Password too short! Please choose a password at least %d characters long.'
                        % self.min_password_length
                    )
                    self.log.error(handler.custom_login_error)
                    return None
                db[username] = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

        return username


    def delete_user(self, user):
        """
        When user is deleted, remove their entry from password db.

        This lets passwords be reset by deleting users.
        """
        try:
            with dbm.open(self.dbm_path, 'c', 0o600) as db:
                del db[user.name]
        except KeyError:
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
        with dbm.open(self.dbm_path, "c", 0o600) as db:
            db[username] = bcrypt.hashpw(new_password.encode("utf8"), bcrypt.gensalt())
        login_msg = "Your password has been changed successfully!"
        self.log.info(login_msg)
        return login_msg


    def get_handlers(self, app):
        return [(r'/login', CustomLoginHandler), (r'/auth/change-password', ResetPasswordHandler)]
