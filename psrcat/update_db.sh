#! /usr/bin/env bash

# over writes existing file
curl https://www.atnf.csiro.au/research/pulsar/psrcat/downloads/psrcat_pkg.tar.gz -o psrcat_pkg.tar.gz

# overwrites existing db
tar -xvf psrcat_pkg.tar.gz psrcat_tar/psrcat.db 

# note when we last updated the files
echo "Updated db on $(date --utc)" >> update_db.log
