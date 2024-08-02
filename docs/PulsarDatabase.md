# Updating the Pulsar database

To make queries for pulsars faster, the [ATNF pulsar catalogue](https://www.atnf.csiro.au/research/pulsar/psrcat/) has been duplicated within the GleamXGPMonitoring app.
The Pulsar model has the following fields:

- name
- decj
- raj
- DM
- p0
- s400

The `name` is unique across all Pulsars, and every pulsar has at least an raj/decj.
Other fields are filled if they are present in the ATNF pulsar catalogue.

Since the pulsar catalogue is periodically updated, a script has been created that will automate the process of retrieving the updated catalogue, and updating the Pulsar table within the GleamXGPMonitoring app.

To run the script, you need to ssh into the machine that is running the app and then run the following:

```bash
docker compose exec web manage.py refresh_pulsar_table
```

**NB**: The current [ATNF website](https://www.atnf.csiro.au/research/pulsar/psrcat/download.html) distributes a file called 'psrcat.db' which, despite the file extension, is NOT a database, but text file containing records for each pulsar.
In the event that the format of this file changes the above script will likely fail.
