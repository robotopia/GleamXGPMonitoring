import os

from . import ADDITIONAL_APPS, BASE_DIR, DJANGO_APPS

SITE_IDENTIFIER = "example.com"
SITE_TITLE = "example.com"
SITE_DESCRIPTION = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua."
SITE_LICENSE = "CC0"
SITE_CREATOR = "Anna Admin"
SITE_CONTACT = {
    "name": "Anna Admin",
    "address": "Example Road 1",
    "email": "admin@example.com",
    "telephone": "+01 234 56789",
}
SITE_PUBLISHER = "At vero eos et accusam"
SITE_CREATED = "2019-01-01"
SITE_UPDATED = "2019-04-01"


INSTALLED_APPS = (
    DJANGO_APPS
    + [
        "daiquiri.auth",
        "daiquiri.conesearch",
        "daiquiri.contact",
        "daiquiri.core",
        "daiquiri.datalink",
        "daiquiri.files",
        "daiquiri.jobs",
        "daiquiri.metadata",
        "daiquiri.oai",
        "daiquiri.query",
        "daiquiri.registry",
        "daiquiri.serve",
        "daiquiri.stats",
        "daiquiri.tap",
        "daiquiri.uws",
    ]
    + ADDITIONAL_APPS
)

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0"]

ACCOUNT_EMAIL_VERIFICATION = "none"
