# JupyterHub First Use Authenticator #

A JupyterHub Authenticator that lets users set their password when they first login. 

Very useful for transient JupyterHubs being used from a single physical location (such as a workshop), where multiple users need to log in but do not have a pre-existing authentication setup. With this, they can just pick a username and password and go!

## Installation ##

You can install this authenticator with:

```bash
pip install jupyterhub-firstuseauthenticator
```

Once installed, you can have JupyterHub use it by adding the following to your `jupyterhub_config.py` file:

```python
c.JupyterHub.authenticator_class = 'firstuseauthenticator.FirstUseAuthenticator'
```

## Configuration ##

It works out of the box as advertized. There is one configuration parameter you can tweak.

### FirstUseAuthenticator.dbm_path ###

Path to the [dbm](https://docs.python.org/3.1/library/dbm.html) file used to store usernames and passwords. Put this somewhere where regular users do not have read/write access to it.

Defaults to `passwords.dbm` in the current directory from which JupyterHub is spawned.
