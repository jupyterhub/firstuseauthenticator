import os

from setuptools import setup, find_packages

# Get the current package version.
here = os.path.abspath(os.path.dirname(__file__))
version_ns = {}
with open(os.path.join(here, 'firstuseauthenticator', '_version.py')) as f:
    exec(f.read(), {}, version_ns)

setup(
    name='jupyterhub-firstuseauthenticator',
    version=version_ns['__version__'],
    description='JupyterHub Authenticator that lets users set passwords on first use',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jupyterhub/firstuseauthenticator",
    author="Yuvi Panda, Project Jupyter Contributors",
    author_email="yuvipanda@gmail.com",
    license="BSD-3-Clause",
    python_requires=">=3.6",
    packages=find_packages(),
    entry_points={
        "jupyterhub.authenticators": [
            "firstuse = firstuseauthenticator:FirstUseAuthenticator",
            "firstuseauthenticator = firstuseauthenticator:FirstUseAuthenticator",
        ],
    },
    install_requires=['bcrypt', 'jupyterhub>=1.3'],
    package_data={
        '': ['*.html'],
    },
)
