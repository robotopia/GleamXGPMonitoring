Database Installation
=====================

Dependancies
------------

For Ubuntu or Debian Linux:

.. code-block::

   sudo apt-get update
   sudo apt-get install postgresql postgresql-contrib libpq-dev python3-dev graphviz python3-pip gosu postgresql-q3c locales

Then install the python requirements (recommended in its own virtual environment) using:

.. code-block::

   pip install -r gleam_webapp/requirements.txt

You will also need to install django-q3c which is currently private so you will need to ask to get access from the `Data Central team <https://datacentral.org.au/about/>`_ (such as James Tocknell).

Environment Variables
---------------------

To run the web application, you will need to set the following environment variables (conda can make these `environment specific <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#setting-environment-variables>`_):

.. csv-table:: Envionment Variables
   :header: "Variable","Description"

   "DB_USER","Postgres user name which you will set in the next section."
   "DB_PASSWORD","Postgres password which you will set in the next section."
   "DB_SECRET_KEY", "Django secret key. `Here <https://saasitive.com/tutorial/generate-django-secret-key/>`_ is a description of how to generate one."


Start the Postgres Database
---------------------------

The following commands will set up the Postgres database for the web app. Replace $DB_USER and $DB_PASSWORD with the environment variable values.

.. code-block::

   sudo -u postgres psql

   CREATE DATABASE mwa_image_plane_db;
   CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';

   ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
   ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
   ALTER ROLE $DB_USER SET timezone TO 'UTC';


.. _create_database:

Setup database for the first time
---------------------------------

Run the following commands from the gleam_webapp subdirectory so Django can setup up the database structure and upload defaults

.. code-block::

   python manage.py makemigrations candidate_app
   python manage.py migrate candidate_app
   python manage.py migrate
   python manage.py migrate --run-syncdb


Create a superuser
-------------------

These commands will set up a superuser account.

.. code-block::

   python manage.py createsuperuser

Set up Q3C
----------
`Q3C <https://github.com/segasai/q3c>`_ allows spatial indexing on a sphere so that you can do quick cone searchs to find nearby sources/candidates within your database.
The followinng commands will set it up:


.. code-block::

   sudo -u postgres psql

   \c mwa_image_plane_db
   CREATE EXTENSION q3c;
   CREATE INDEX ON candidate_app_candidate (q3c_ang2ipix(ra_deg, dec_deg));

Delete Postgres Database
------------------------

Only do this is you want to restart the database!

To delete the database use the following commands

.. code-block::

   sudo -u postgres psql

   DROP DATABASE mwa_image_plane_db;
   CREATE DATABASE mwa_image_plane_db;

You will then have to recreate the database using the commands in :ref:`create_database`
