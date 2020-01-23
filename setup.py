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
    url='https://github.com/yuvipanda/jupyterhub-firstuseauthenticator',
    author='Yuvi Panda',
    author_email='yuvipanda@gmail.com',
    license='3 Clause BSD',
    packages=find_packages(),
    install_requires=['bcrypt', 'jupyterhub>=0.8'],
    package_data={
        '': ['*.html'],
    },
)
