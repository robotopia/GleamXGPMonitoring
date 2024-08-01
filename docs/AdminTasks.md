(admin)=

# Admin tasks

When the app is first created a superuser account will be created so that you have at least one valid login to add new users.
Details of the superuser name/password can be found in the [quick start](quick_start.md#settings-files) guide.

All the tasks listed on this page require that you have an admin account which could be the superuser account noted above, or (preferably) a user account with "Staff Status".

To login to the admin pages you'll navigate to the `/admin` site (e.g. `http://mwa-image-plane.duckdns.org/admin`).
There is no link to this page from the web-app, you'll need to type this into your browser directly.

On the left pane you should see three sections:

![Admin Pages](figures/AdminPages.png)

Each of the rows correspond to a model in the database.
The groups represent the different 'apps' that are installed.

(addusers)=

## Add new users to the app

Navigate to the admin page at `<site url>/admin`.
If you are not logged in, then you’l be prompted to login.
A default admin account is created during the deployment process see [this page](Architecture.md) for details including the default admin user/pass.
You should see an admin page with the following section:

![Admin Auth Section](figures/AdminAuthSection.png)

Click on the `+ Add` button next to the `Users` section.

On this page you’ll be asked to give a username and password for the new user.

Click on the “Save” button and you’ll be then taken to a page that lets you edit the profile of that user.
By default all users are given permissions of just “Active” which means they can log into the web app and navigate the html pages.
If you want someone to be able to admin the site (e.g. log into the admin pages), then you’ll have to set their permissions to include “Staff Status”.
