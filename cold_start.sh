#! /usr/bin/env bash

# set up the psr databse
cd psrcat
./update_db.sh
cd ..

# apply migrations and add an admin user
./migrate.sh
./make_admin.sh

# install the q3c extension to our db
./enable_q3c.sh

# # load fixtures
for fixture in observation.json \
               project.json \
               filter.json \
               classification.json \
               candidate.json
do 
    echo "Lading fixture ${fixture}"
    docker-compose exec web python manage.py loaddata ${fixture}
done