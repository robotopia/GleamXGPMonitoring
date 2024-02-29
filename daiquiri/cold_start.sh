#! /usr/bin/env bash
python manage.py migrate                   # initializes the web database
python manage.py migrate --database tap    # initializes the tap schema in the scientific db
python manage.py migrate --database oai    # initializes the oai schema in the scientific db
python manage.py createsuperuser --noinput # creates an admin user
python manage.py download_vendor_files     # dowloads front-end files from the CDN