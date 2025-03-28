# Quick Start Guide

## Clone the git repo

The source code for this app is hosted on the GitHub page.
To develop locally, you can clone the repository from [https://github.com/ADACS-Australia/GleamXGPMonitoring](https://github.com/ADACS-Australia/GleamXGPMonitoring).

## Build and start docker containers

Clone the git repository (see above) and navigate to the root directory.

For the development deployment run:

```shell
docker compose -f docker-compose.yml up --build
```

For the production deployment run:

```shell
docker compose -f docker-compose.prod.yml up --build
```

The `--build` flag will rebuild any containers that need to be updated, the first time you run the web the containers will be either built from scratch or pulled from docker hub.

Once started you will be able to access the web app using `http://localhost`.

## Settings Files

The following files are used to control the behavior of the web app:

- `.env.dev` and `.env.prod`
- `.env.dev.db` and `.env.prod.db`
- `gleam_webapp/gleam_wabapp/settings.py`

The `.env.*` files control the environment variables that are set within the containers.
The `.dev` files are used for a local development version of the app, which is a simpler deployment that live updates when you change files, and will give a full debug on errors.
The `.prod` files are for a production deployment and include a proper web server, a reverse proxy, and a few other security features.
Please note that the `prod` files **should not be committed to your git repo** (which is why you wont' see them when you clone the repo from github).

`.env.{dev,prod}` will set the following variables within the “web” container (below are the defaults for .dev file):

```shell
# DJango settings
DEBUG=1
SECRET_KEY=foo
DJANGO_LOG_LEVEL=INFO
DJANGO_ALLOWED_HOSTS=localhost 0.0.0.0 [::1] mwa-image-plane.duckdns.org
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=test
DJANGO_SUPERUSER_EMAIL=none@nothing.com
DJANGO_SECRET_KEY=devkey
# PostgreSQL settings
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=gleamx
SQL_USER=gleamer
SQL_PASSWORD=gleamxgp123%rg
SQL_HOST=db
SQL_PORT=5432

```

The `.env.{dev,prod}.db` file sets environment variables within the database container (again the .dev version below):

```shell
# Development settings for the database
POSTGRES_DB=gleamx
POSTGRES_USER=gleamer
POSTGRES_PASSWORD=gleamxgp123%rg
```

The user/pass/db in the `env.{dev,prod}.db` file needs to agree with the `SQL_{USER/PASSWORD/HOST}` in the corresponding `.env.{dev,prod}` file.

The `settings.py` file is used by DJango to configure the web app.
This file doesn’t need to be edited as it will read the various settings from the environment variables that are set in the web container.
