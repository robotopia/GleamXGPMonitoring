(managedockercontainers)=

# How to manage Docker containers

## Update the code that is running the web app

The code that runs within the web app is not included in the "web" container.
The code is on the host machine in the root of the git repo.
If you cloned from github without specifying a new directory name this directory will be `GleamXGPMonitoring`.
Any changes that you make to the code within this repository will visible to the web service running the app.
However, depending on how you are running the app, the changes may not be automatically reflected in the app immediately.

If you are running a [development deployment](Architecture.md#development-deployment), then you should see a message from docker-compose that looks like this:

```output
web_1  | /home/app/web/<app>/views.py changed, reloading.
web_1  | 2023-11-28 04:24:54,283 INFO /home/app/web/<app>/views.py changed, reloading.
web_1  | Watching for file changes with StatReloader
web_1  | 2023-11-28 04:24:54,878 INFO Watching for file changes with StatReloader
web_1  | Performing system checks...
```

This tells you that some python code has been changed (`views.py` in this case), and so the web app will restart itself.
Changing static files or templates doesn’t require any reload of the web app so you won’t see the above message.

If you are running a [production deployment](Architecture.md#production-deployment), then the app will NOT automatically reload or apply changes.
In this case you have to restart the web app using `docker-compose restart web`.
If you have made changes to static files or templates then you’ll have to also run `docker-compose exec web python manage.py collectstatic --noinput` so that the static files are updated.

## Restart a stopped or broken instance of the web app

In most cases you’ll just need to restart the container hosting the web app using `docker-compose restart web`.

If this doesn’t work then you can bring down all the containers and restart them using `docker-compose down` and `docker-compose -f docker-compose{.prod}.yml up` (depending on wether you are running the prod or dev version).

## Clear the database and start “fresh”

There are two ways to do this.

### The friendly way

Run `docker-compose exec web python manage.py flush` which will delete the data from the tables managed by DJango.
This doesn’t undo any migrations, and leaves the db schema in tact.
To rebuild from here:

1. Load default data from fixtures:
   - `docker-compose exec web python manage.py loaddata <fixture>.json --app <app>.<table>`
2. Create a super user (admin) account:
   - `docker-compose exec web python manage.py createsuperuser --noinput`

### The not-friendly way

Run `docker-compose down -v`, which brings down all the containers, all the networks, and deletes the associated volumes.
You will loose all data associated with the app: tables, schema, user accounts, static files.
To rebuild from here:

1. Start the web app using
   `docker-compose -f docker-compse{.prod}.yml up` (depending on whether you are running id dev/prod)
2. (in different terminal) Collect the static files using
   `docker-compose exec web python manage.py collectstatic --noinput`
3. Create and run all migrations:
   - `docker-compose exec web python manage.py makemigrations`
   - `docker-compose exec web python manage.py migrate`
4. Load default data from fixtures:
   - `docker-compose exec web python manage.py loaddata <fixture>.json --app <app>.<table>`
5. Create a super user (admin) account:
   - `docker-compose exec web python manage.py createsuperuser --noinput`
