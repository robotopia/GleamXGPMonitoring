# GleamXGPMonitoring
GLEAM Galactic Plane transient rating app is a web-based candidate classifier for team members to easily classify transient candidates. The transient candidates are detected in the MWA's weekly monitoring of the galactic plane.


## Restarting after Nimbus has been shut down

nginx is automatically started when the instance reboots and it intercepts all the web traffic before it gets to our website. In order to stop nginx you need to ssh into the ubuntu vm and type `sudo service nginx stop`.

Once the nginx service has been stopped you can start the web service using docker via `docker compouse up -d` whilst in the directory `/home/ubuntu/GleamXGPMonitoring`.
