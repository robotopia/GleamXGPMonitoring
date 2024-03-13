#! /usr/bin/env bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py makemigrations candidate_app
docker compose exec web python manage.py migrate
