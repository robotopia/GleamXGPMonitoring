import django_filters
from .models import Candidate


class CandidateFilter(django_filters.FilterSet):
    id = django_filters.NumericRangeFilter(field_name="id", label="Candidate ID")
    can_det_stat = django_filters.NumericRangeFilter(
        field_name="can_det_stat", label="Detection Statistic"
    )
    obs_id = django_filters.NumericRangeFilter(
        field_name="obs_id__observation_id",
        label="OBSID",
    )
    ra_deg = django_filters.NumericRangeFilter(
        field_name="ra_deg", label="RA (degrees)"
    )
    dec_deg = django_filters.NumericRangeFilter(
        field_name="dec_deg", label="DEC (degrees)"
    )
    can_fluence = django_filters.NumericRangeFilter(
        field_name="can_fluence", label="Fluence (Jy.s)"
    )

    class Meta:
        model = Candidate
        fields = []
