# ZaPF OAuth Provider

[![Code Climate](https://codeclimate.com/github/ZaPF/account_management/badges/gpa.svg)](https://codeclimate.com/github/ZaPF/account_management) [![Issue Count](https://codeclimate.com/github/ZaPF/account_management/badges/issue_count.svg)](https://codeclimate.com/github/ZaPF/account_management)

## Deployment

To deploy the flask app you can use the configuration and systemd service for a gunicorn provided in the
repository. The gunicorn creates in the default configuration a socket that can be used by a proxy
daemon like nginx to deploy the app to the internet. The proxy daemon also would be responsible
for stuff like SSL encryption.

### Environment Variables

Variable        | Description
----------------|----------------------------------------------------
`AUTH_SETTINGS` | A path to a config file that overrides the defaults

## Commands

Apart from the usual `manage.py runserver` and `manage.py shell`, the following
commands are supported:

* `manage.py createuser uid FirstName Surname [email] [password]` - create a user
* `manage.py delete_user uid` - delete a user
* `manage.py passwd uid` - change a password for the user
* `manage.py sanity` - runs sanity checks, like checking that the base DN's for
  different things exist, and creates them if necessary
* `manage.py groups`  - lists groups
* `manage.py members group_name` - list members in a group
* `manage.py newgroup group_name` - create a group
* `manage.py delgroup group_name` - delete a group
* `manage.py join username group_name` - add a user to a group
* `manage.py remove username group_name` - remove a user from a group

## OpenLDAP notes

### Schema
The following schema are required:
  * `core`
  * `inetOrgPerson`
  * `cosine`
  * `nis`
  * [`oidc-schema`](https://bitbucket.org/connect2id/openid-connect-ldap-schema/wiki/Home)

### ACL's
Please make sure the bind user can bind and has read&write access to the users,
groups, and oauth2 subtrees.

### Good hashing
Using the `contrib/sha2` module for OpenLDAP is highly recommended, otherwise
the following hashes do not work:
  * `HASHED_SHA256`
  * `HASHED_SHA385`
  * `HASHED_SHA512`
  * `HASHED_SALTED_SHA256`
  * `HASHED_SALTED_SHA385`
  * `HASHED_SALTED_SHA512`

### Testing
A [sample OpenLDAP configuration](test/OpenLDAP/slapd.conf) to run a testing
server is included.
Tests hoever are run by [mocking](http://ldap3.readthedocs.io/mocking.html) the
ldap connection. A [script](test/make_ldap_json.py) is included to generate the
serialized data objects used from a [LDIF file](test/data.ldif).
