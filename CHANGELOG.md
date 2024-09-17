# Changes in firstuseauthenticator

For detailed changes from the prior release, click on the version number, and
its link will bring up a GitHub listing of changes. Use `git log` on the
command line for details.

## 1.1

### [1.1.0] - 2024-09-17

#### Enhancements made

- default: allow all users if allowed_users is unspecified [#56](https://github.com/jupyterhub/firstuseauthenticator/pull/56) ([@minrk](https://github.com/minrk), [@consideRatio](https://github.com/consideRatio))
- Register authentication class with jupyterhub [#53](https://github.com/jupyterhub/firstuseauthenticator/pull/53) ([@consideRatio](https://github.com/consideRatio), [@minrk](https://github.com/minrk))

#### Continuous integration improvements

- ci: refresh github workflows [#57](https://github.com/jupyterhub/firstuseauthenticator/pull/57) ([@consideRatio](https://github.com/consideRatio))

#### Contributors to this release

The following people contributed discussions, new ideas, code and documentation contributions, and review.
See [our definition of contributors](https://github-activity.readthedocs.io/en/latest/#how-does-this-tool-define-contributions-in-the-reports).

([GitHub contributors page for this release](https://github.com/jupyterhub/firstuseauthenticator/graphs/contributors?from=2021-10-28&to=2024-09-17&type=c))

@consideRatio ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Ffirstuseauthenticator+involves%3AconsideRatio+updated%3A2021-10-28..2024-09-17&type=Issues)) | @minrk ([activity](https://github.com/search?q=repo%3Ajupyterhub%2Ffirstuseauthenticator+involves%3Aminrk+updated%3A2021-10-28..2024-09-17&type=Issues))

## 1.0

### [1.0.0] - 2021-10-27

1.0 fixes a critical security vulnerability when `create_users = True` (default behavior)
where unauthorized users could gain access to other users' jupyterhub accounts, if usernames are known.

Disabling the creation of new users with `c.FirstUseAuthenticator.create_users = False` mitigates this attack while waiting for upgrade.

#### Bugs fixed

- Revert authenticate being made sync from async [#45](https://github.com/jupyterhub/firstuseauthenticator/pull/45) ([@consideRatio](https://github.com/consideRatio))
- normalize username to lock password [#38](https://github.com/jupyterhub/firstuseauthenticator/pull/38) ([@georgejhunt](https://github.com/georgejhunt))
- Fix failure to await render_template [#37](https://github.com/jupyterhub/firstuseauthenticator/pull/37) ([@georgejhunt](https://github.com/georgejhunt))
- Fix bug where create_users and password requirement couldn't work together [#33](https://github.com/jupyterhub/firstuseauthenticator/pull/33) ([@saisiddhant12](https://github.com/saisiddhant12))

#### Maintenance and upkeep improvements

- Refactoring for readability [#46](https://github.com/jupyterhub/firstuseauthenticator/pull/46) ([@consideRatio](https://github.com/consideRatio))
- update package metadata to require Python 3.6 [#41](https://github.com/jupyterhub/firstuseauthenticator/pull/41) ([@minrk](https://github.com/minrk))

## Documentation improvements

- Add GitHub CI badge to README [#47](https://github.com/jupyterhub/firstuseauthenticator/pull/47) ([@consideRatio](https://github.com/consideRatio))

#### Other merged PRs

- Update master to main [#44](https://github.com/jupyterhub/firstuseauthenticator/pull/44) ([@consideRatio](https://github.com/consideRatio))
- run tests on GHA [#40](https://github.com/jupyterhub/firstuseauthenticator/pull/40) ([@minrk](https://github.com/minrk))

#### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyterhub/firstuseauthenticator/graphs/contributors?from=2020-03-18&to=2021-10-26&type=c))

[@consideRatio](https://github.com/search?q=repo%3Ajupyterhub%2Ffirstuseauthenticator+involves%3AconsideRatio+updated%3A2020-03-18..2021-10-26&type=Issues) | [@georgejhunt](https://github.com/search?q=repo%3Ajupyterhub%2Ffirstuseauthenticator+involves%3Ageorgejhunt+updated%3A2020-03-18..2021-10-26&type=Issues) | [@minrk](https://github.com/search?q=repo%3Ajupyterhub%2Ffirstuseauthenticator+involves%3Aminrk+updated%3A2020-03-18..2021-10-26&type=Issues) | [@saisiddhant12](https://github.com/search?q=repo%3Ajupyterhub%2Ffirstuseauthenticator+involves%3Asaisiddhant12+updated%3A2020-03-18..2021-10-26&type=Issues)

## 0.14

### [0.14.1] - 2020-03-18

* Fix login error msg [#30](https://github.com/jupyterhub/firstuseauthenticator/pull/30) ([@GeorgianaElena](https://github.com/GeorgianaElena))

### [0.14.0] - 2020-03-03

* Update badges and add long description to pypi [#28](https://github.com/jupyterhub/firstuseauthenticator/pull/28) ([@GeorgianaElena](https://github.com/GeorgianaElena))
* Set minimum length on passwords [#21](https://github.com/jupyterhub/firstuseauthenticator/pull/21) ([@GeorgianaElena](https://github.com/GeorgianaElena))


## 0.13

### [0.13.0] - 2020-01-07

* fixed 'change password' feature for Jupyterhub version 1.0.0 [#23](https://github.com/jupyterhub/firstuseauthenticator/pull/23) ([@ABVitali](https://github.com/ABVitali))
* Update packages in tests [#22](https://github.com/jupyterhub/firstuseauthenticator/pull/22) ([@minrk](https://github.com/minrk))

## 0.12

### [0.12.0] - 2019-01-24

* Catch deletion of users that have not logged in [#16](https://github.com/jupyterhub/firstuseauthenticator/pull/16) ([@willirath](https://github.com/willirath))

## 0.11

### [0.11.1] - 2019-01-24

* add missing parameter to call of validate_user() [#12](https://github.com/jupyterhub/firstuseauthenticator/pull/12) ([@stv0g](https://github.com/stv0g))
* add name sanitization [#11](https://github.com/jupyterhub/firstuseauthenticator/pull/11) ([@leportella](https://github.com/leportella))
* add question on how to change password [#10](https://github.com/jupyterhub/firstuseauthenticator/pull/10) ([@leportella](https://github.com/leportella))
* add basic tests [#9](https://github.com/jupyterhub/firstuseauthenticator/pull/9) ([@minrk](https://github.com/minrk))
* Add option to change password [#8](https://github.com/jupyterhub/firstuseauthenticator/pull/8) ([@leportella](https://github.com/leportella))
* Clean password db when user is deleted [#7](https://github.com/jupyterhub/firstuseauthenticator/pull/7) ([@yuvipanda](https://github.com/yuvipanda))

### [0.11.0] - 2018-09-04

* First release

[1.1.0]: https://github.com/jupyterhub/firstuseauthenticator/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/jupyterhub/firstuseauthenticator/compare/v0.14.1...v1.0.0
[0.14.1]: https://github.com/jupyterhub/firstuseauthenticator/compare/v0.14.0...v0.14.1
[0.14.0]: https://github.com/jupyterhub/firstuseauthenticator/compare/0.13.0...v0.14.0
[0.13.0]: https://github.com/jupyterhub/firstuseauthenticator/compare/v0.12...0.13.0
[0.12.0]: https://github.com/jupyterhub/firstuseauthenticator/compare/v0.11...v0.12
[0.11.1]: https://github.com/jupyterhub/firstuseauthenticator/compare/v0.11...v0.11.1

