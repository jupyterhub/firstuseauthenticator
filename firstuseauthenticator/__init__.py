"""
JupyterHub Authenticator to let users set their password on first use.

After installation, you can enable this with:

```
c.JupyterHub.authenticator_class = 'firstuseauthenticator.FirstUseAuthenticator'
```
"""
from firstuseauthenticator.firstuseauthenticator import FirstUseAuthenticator

__all__ = [FirstUseAuthenticator]
