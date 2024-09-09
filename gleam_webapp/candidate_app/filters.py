import django_filters
from django.db.models import Q, F
from .models import Candidate
from django_q3c.expressions import Q3CRadialQuery, Q3CDist

from astropy.coordinates import SkyCoord
import astropy.units as u
import logging

logger = logging.getLogger(__name__)


class CandidateFilter(django_filters.FilterSet):
    id = django_filters.RangeFilter(field_name="id", label="Candidate ID")
    can_det_stat = django_filters.NumericRangeFilter(
        field_name="can_det_stat", label="Detection Statistic"
    )
    obs_id = django_filters.RangeFilter(
        field_name="obs_id__observation_id",
        label="OBSID",
    )
    ra_deg = django_filters.CharFilter(
        field_name="ra_deg",
        label="RA (deg or hms)",
        method="no_filter",
    )
    dec_deg = django_filters.CharFilter(
        field_name="dec_deg",
        label="DEC (deg or dms)",
        method="no_filter",
    )
    radius = django_filters.NumberFilter(
        label="radius (arcmin)", method="filter_by_cone_search"
    )

    can_fluence = django_filters.RangeFilter(
        field_name="can_fluence", label="Fluence (Jy.s)"
    )

    class Meta:
        model = Candidate
        fields = []

    def no_filter(self, qs, name, value):
        """
        Over-ride whatever filtering would have taken place
        """
        return qs

    def filter_by_cone_search(self, queryset, name, value):
        # logger.warning(f"QS size is {queryset.count()}")

        if not value:
            return queryset

        ra_center = self.data.get("ra_deg")
        dec_center = self.data.get("dec_deg")

        if (len(ra_center) == 0) or (len(dec_center) == 0):
            return queryset

        try:
            ra_center = float(ra_center)
            dec_center = float(dec_center)
        except ValueError as e:
            if "convert string" in str(e):
                # User may have submitted RA/DEC in HMS/DMS
                try:
                    coord = SkyCoord(
                        ra_center, dec_center, unit=(u.hourangle, u.deg), frame="fk5"
                    )
                    ra_center = coord.ra.degree
                    dec_center = coord.dec.degree
                except ValueError:
                    logger.warning("CAUGHT ERROR setting ra/dec to zero")
                    ra_center = 0
                    dec_center = 0
            else:
                raise e

        radius = float(value) / 60.0  # arcmin

        logger.warning(f"ra {ra_center}, dec {dec_center}, radius {radius}")
        # Use Q3C spatial query for the cone search
        qs = queryset.filter(
            Q(
                Q3CRadialQuery(
                    center_ra=ra_center,
                    center_dec=dec_center,
                    ra_col="ra_deg",
                    dec_col="dec_deg",
                    radius=radius,
                )
            )
        )
        qs = qs.annotate(  # do the distance calcs in the db
            sep=Q3CDist(
                ra1=F("ra_deg"),
                dec1=F("dec_deg"),
                ra2=ra_center,
                dec2=dec_center,
            )
            * 60  # deg -> arcmin
        ).order_by("sep")
        return qs
