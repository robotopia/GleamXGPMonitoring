from django.http import HttpResponse
from astropy.table import Table
import numpy as np
import io


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
