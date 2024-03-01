#! /usr/bin/env bash

# set up the psr databse
cd psrcat
./update_db.sh
cd ..

# build / start the web app
docker-compose -f docker-compose.yml up --build -d

# apply migrations and add an admin user
./migrate.sh
./make_admin.sh

# install the q3c extension to our db
./enable_q3c.sh

# # load fixtures
# docker-compose exec web python gleam_webapp/manage.py loaddata auth.json
# docker-compose exec web python gleam_webapp/manage.py loaddata app.json