from setuptools import setup, find_packages

setup(
    name='jupyterhub-firstuseauthenticator',
    version='0.9',
    description='JupyterHub Authenticator that lets users set passwords on first use',
    url='https://github.com/yuvipanda/jupyterhub-firstuseauthenticator',
    author='Yuvi Panda',
    author_email='yuvipanda@gmail.com',
    license='3 Clause BSD',
    packages=find_packages(),
    install_requires=['bcrypt']
)
