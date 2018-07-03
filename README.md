# JupyterHub First Use Authenticator #

A [JupyterHub](https://jupyterhub.readthedocs.io) authenticator that helps new users set their password on their first login to JupyterHub.

**Are you running a workshop from a single physical location, such as a university seminar or a user group?**

JupyterHub First Use Authenticator can simplify the user set up for you. It's very useful when using transient
JupyterHub instances in a single physical location. It allows multiple users to log in, but you do not have install a pre-existing authentication setup. With this authenticator, users can just pick a username and password and get to work!

## Installation ##

You can install this authenticator with:

```bash
pip install jupyterhub-firstuseauthenticator
```

Once installed, configure JupyterHub to use it by adding the following to your `jupyterhub_config.py` file:

```python
c.JupyterHub.authenticator_class = 'firstuseauthenticator.FirstUseAuthenticator'
```

## Configuration ##

### FirstUseAuthenticator.dbm_path ###

Path to the [dbm](https://docs.python.org/3.5/library/dbm.html) file, or a UNIX database file such as `passwords.dbm`, used to store usernames and passwords. The dbm file should be put where regular users do not have read/write access to it.

This authenticator's default setting for the path to the `passwords.dbm` is the current directory from which JupyterHub is spawned.

### FirstUseAuthenticator.create_users ###

Create users if they do not exist already.

When set to False, users would have to be explicitly created before
they can log in. Users can be created via the admin panel or by setting
whitelist / admin list.

Defaults to True.
