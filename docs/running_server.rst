Running Server
==============


Checking for errors and inspecting logs
---------------------------------------
nginx errors are in
.. code-block::

   tail -f cat /var/log/nginx/error.log

All commands assume you're in the gleam_webapp sub directory. You can see the output of the server with

.. code-block::

   tail -f uwsgi-emperor.log

.. _start_server:

Starting the server
-------------------

Start the uwsgi server with

.. code-block::

   cd /home/ubuntu/GleamXGPMonitoring/gleam_webapp
   uwsgi --ini gleam_webapp.ini

This will run in the background and the following sections describe how to restarting and stopping the server.


Restarting the server
---------------------

.. code-block::

   kill -HUP `cat /tmp/project-master.pid`


Stopping the server
-------------------

.. code-block::

   uwsgi --stop /tmp/project-master.pid


Installing updates
------------------

If the updates are small normally something as simple as the following will suffice:

.. code-block::

   git pull
   kill -HUP `cat /tmp/project-master.pid`

Larger updates may need a combination of the following commands

.. code-block::

   git pull
   # Stop server
   uwsgi --stop /tmp/project-master.pid
   # Check for new dependent software
   pip install -r requirements.txt
   # Check for new static files
   python manage.py collectstatic
   # Make any required changes to the backend database
   python manage.py makemigrations
   python manage.py migrate
   # Start server
   uwsgi --ini gleam_webapp.ini




