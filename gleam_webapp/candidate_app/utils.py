from django.http import HttpResponse
from astropy.table import Table
from datetime import datetime
import numpy as np
import io
import logging

logger = logging.getLogger(__name__)


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

    # conver datetime columns into strings
    for c in data.colnames:
        if data[c].dtype == datetime:
            data[c] = data[c].astype(str)

    memfile = io.BytesIO()
    data.write(memfile, format="fits")

    response = HttpResponse(memfile.getvalue(), content_type="application/fits")
    response["Content-Disposition"] = f'attachment; filename="{table}.fits"'

    return response
