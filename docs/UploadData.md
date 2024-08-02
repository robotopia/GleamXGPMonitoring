# Uploading Data

To upload data into the webapp you need to use the `upload_cand.py` script.
This script is in the `gleam_webapp/` directory, and requires [Astropy](https://www.astropy.org/) to be installed.

The operation of the script is described by it's help:

```output
usage: upload_cand.py [-h] [--data_directory DATA_DIRECTORY] [--fits FITS] [-L {DEBUG,INFO,WARNING}]

Upload a GLEAM transient candidate to the database.

optional arguments:
  -h, --help            show this help message and exit
  --data_directory DATA_DIRECTORY
                        Path to directory containing all of the gifs and images.
  --fits FITS           Optional option to specify a fits file. If not used, will get all fits files in the data_directory
  -L {DEBUG,INFO,WARNING}, --loglvl {DEBUG,INFO,WARNING}
                        Logger verbosity level. Default: INFO
```

A few things not described by the help are:

1. You need to have the following environment variables defined:
   - `SYSTEM_ENV` (optional) if this is set to "DEVELOPMENT" then it will set the website url to be your local machine, otherwise it'll assume the live site url.
   - `IMAGE_PLANE_TOKEN` needs to be set to a valid access token. (see [the user guide](UserGuide) for managing tokens)
2. The FITS file provided to `--fits` needs to be a table with one row per `candidate`.
   - The required/accepted fields are listed on the [databases](databases.md) page
   - Instead of `projectid` which is an int in the database, you should supply a column `project` which is the project name
   - Instead of `filterid` which is an int in the database, you should supply a column `filter` which is the filter name
   - `ra_hms` and `dec_hms` are computed automatically so don't need to be supplied
   - `png_path` and `gif_path` don't need to be supplied in the table, the paths are assumed to be `DATA_DIRECTORY/<obsid>/<filter_id>/<cand_id>.{png,gif}` where `filter_id` and `cand_id` are columns in the fits table (which are not stored in the db!).
   - The column `metadata` (if present) will be used to create a new `metadata` object which is then linked to the given `candidate`
