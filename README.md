# ZaPF Anmeldesystem

[![Code Climate](https://codeclimate.com/github/ZaPF/anmeldesystem/badges/gpa.svg)](https://codeclimate.com/github/ZaPF/anmeldesystem)

Referenzimplementation für Sommer17 in Berlin

## Deployment

To deploy the flask app you can use the configuration and systemd service for a gunicorn provided in the
repository. The gunicorn creates in the default configuration a socket that can be used by a proxy
daemon like nginx to deploy the app to the internet. The proxy daemon also would be responsible
for stuff like SSL encryption.

### Environment Variables

Variable                        | Description
--------------------------------|-----------------------------------------------------------
`AUTH_SETTINGS`                 | A path to a config file that overrides the defaults
`OAUTHLIB_INSECURE_TRANSPORT=1` | If necessary (it really shouldn't), allow OAuth2 via HTTP.
