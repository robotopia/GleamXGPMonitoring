

#!/usr/bin/env python

import os
import sys
import argparse
import urllib.request
import requests
import json

from astropy.coordinates import Angle
import astropy.units as u
from astropy.io import fits

import logging
logger = logging.getLogger(__name__)


def getmeta(servicetype='metadata', service='obs', params=None):
    """
    Function to call a JSON web service and return a dictionary:
    Given a JSON web service ('obs', find, or 'con') and a set of parameters as
    a Python dictionary, return a Python dictionary xcontaining the result.
    Taken verbatim from http://mwa-lfd.haystack.mit.edu/twiki/bin/view/Main/MetaDataWeb
    """

    # Append the service name to this base URL, eg 'con', 'obs', etc.
    BASEURL = 'http://ws.mwatelescope.org/'


    if params:
        # Turn the dictionary into a string with encoded 'name=value' pairs
        data = urllib.parse.urlencode(params)
    else:
        data = ''

    try:
        result = json.load(urllib.request.urlopen(BASEURL + servicetype + '/' + service + '?' + data))
    except urllib.error.HTTPError as err:
        logger.error("HTTP error from server: code=%d, response:\n %s" % (err.code, err.read()))
        return
    except urllib.error.URLError as err:
        logger.error("URL or network error: %s" % err.reason)
        return

    return result


def upload_obsid(obsid):
    """ Upload an MWA observation to the database.

    Parameters
    ----------
    obsid : `int`
        MWA observation ID.
    """
    data = getmeta(params={'obsid':obsid})

    # Upload
    session = requests.session()
    session.auth = (os.environ['GLEAM_USER'], os.environ['GLEAM_PASSWORD'])
    url = 'http://127.0.0.1:8000/observation_create/'
    data = {
        'observation_id': obsid,
        'obsname': data['obsname'],
        'starttime': data['starttime'],
        'stoptime': data['stoptime'],
        'ra_tile_dec': data['metadata']['ra_pointing'],
        'dec_tile_dec': data['metadata']['dec_pointing'],
        'ra_tile_hms': Angle(data['metadata']['ra_pointing'], unit=u.deg).to_string(unit=u.hour, sep=':')[:11],
        'dec_tile_dms': Angle(data['metadata']['dec_pointing'], unit=u.deg).to_string(unit=u.deg, sep=':')[:12],
        'projectid': data['projectid'],
        'azimuth': data['metadata']['azimuth_pointing'],
        'elevation': data['metadata']['elevation_pointing'],
        'frequency_channels': str(data['rfstreams']['0']['frequencies']),
        'cent_freq': (data['rfstreams']['0']['frequencies'][0] + data['rfstreams']['0']['frequencies'][-1])*1.28/2,
        'freq_res': data['freq_res'],
        'int_time': data['int_time'],
    }
    r = session.post(url, data=data)

def upload_candidate(image_path, fits_path, filter_id):
    """ Upload an MWA observation to the database.

    Parameters
    ----------
    image : `str`
        The location of the candidate image to upload.
    obsid : `int`
        MWA observation ID.
    filter_id : `int`
        The ID of the filter used to detect this candidate.
    """
    # Set up session
    session = requests.session()
    session.auth = (os.environ['GLEAM_USER'], os.environ['GLEAM_PASSWORD'])
    url = 'http://127.0.0.1:8000/candidate_create/'

    # Read fits file
    hdul = fits.open(fits_path)

    # loop over each candidate
    for cand in hdul[1].data:
        data = {
            "filter_id": filter_id,
        }
        # Loop over each header and append data to the upload dictionary
        for hi, dat in enumerate(cand):
            fits_header = f"TTYPE{hi+1}"
            header = hdul[1].header[fits_header]
            logger.debug(f"{header}: {dat}")
            if header == "obs_cent_freq":
                # Skip because already have that data in obsid
                pass
            elif header == "obs_id":
                # upload obsid
                upload_obsid(dat)
                data[header] = dat
            elif header.endswith("ra_deg"):
                # parse to hms
                data[header] = dat
                hms_header = header[:-3]+"hms"
                data[hms_header] = Angle(dat, unit=u.deg).to_string(unit=u.hour, sep=':')[:11]
            elif header.endswith("dec_deg"):
                # parse to dms
                data[header] = dat
                dms_header = header[:-3]+"dms"
                data[dms_header] = Angle(dat, unit=u.deg).to_string(unit=u.deg, sep=':')[:12]
            else:
                data[header] = dat

        # open the image file
        with open(image_path, 'rb') as image:
            # upload to database
            r = session.post(url, data=data, files={"png":image})
        print(r.text)
        r.raise_for_status()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload a GLEAM transient candidate to the database.')
    parser.add_argument('--image', type=str,
                        help='The location of the image')
    parser.add_argument('--fits', type=str,
                        help='The location of the fits files containing the candidate information.')
    parser.add_argument('--filter', type=str,
                        help='The ID of the filter used for this candidate.')
    args = parser.parse_args()

    upload_candidate(args.image, args.fits, args.filter)