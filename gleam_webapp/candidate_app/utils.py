from django.http import HttpResponse
from astropy.table import Table
import numpy as np
import io


def FITSTableType(val):
    """
    Return the FITSTable type corresponding to each named parameter in obj
    """
    if isinstance(val, bool):
        types = "L"
    elif isinstance(val, (int, np.int64, np.int32)):
        types = "J"
    elif isinstance(val, (float, np.float64, np.float32)):
        types = "E"
    elif isinstance(val, str):
        types = "{0}A".format(len(val))
    else:
        types = "5A"
    return types


def download_fits(request, queryset, table):

    obsids = []
    rating_counts = []
    for c in queryset:
        obsids.append(c.obs_id.observation_id)
        rating_counts.append(c.rating_count)
        print(c.obs_id, c.rating_count)

    print("making table")
    data = Table([obsids, rating_counts])

    print(data)
    memfile = io.BytesIO()
    data.write(memfile, format="fits")

    print("forming response")
    response = HttpResponse(memfile.getvalue(), content_type="application/fits")
    # force download.
    response["Content-Disposition"] = f'attachment; filename="{table}.fits"'

    return response
