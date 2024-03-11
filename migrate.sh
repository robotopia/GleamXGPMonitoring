#! /usr/bin/env bash
docker compose exec web python gleam_webapp/manage.py makemigrations
docker compose exec web python gleam_webapp/manage.py makemigrations candidate_app
docker compose exec web python gleam_webapp/manage.py migrate
