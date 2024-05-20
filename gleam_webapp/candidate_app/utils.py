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

    # Extract all the column names from the model, plus any additional
    # columns we created using annotations
    colnames = [a.name for a in queryset.model._meta.fields] + [
        a for a in queryset.query.annotations.keys()
    ]

    # Extract the values for the columns, converting None->np.nan
    columns = {a: [] for a in colnames}
    for item in queryset.values(*colnames):
        for c in colnames:
            val = item[c]
            columns[c].append(val if val is not None else np.nan)

    # make a table, and write it to memory for downloading.
    data = Table(columns)
    memfile = io.BytesIO()
    data.write(memfile, format="fits")

    response = HttpResponse(memfile.getvalue(), content_type="application/fits")
    response["Content-Disposition"] = f'attachment; filename="{table}.fits"'

    return response
