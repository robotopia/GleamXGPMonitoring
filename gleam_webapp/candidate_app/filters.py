import django_filters
from .models import Candidate


class CandidateFilter(django_filters.FilterSet):
    id = django_filters.RangeFilter(field_name="id", label="Candidate ID")
    can_det_stat = django_filters.NumericRangeFilter(
        field_name="can_det_stat", label="Detection Statistic"
    )
    obs_id = django_filters.RangeFilter(
        field_name="obs_id__observation_id",
        label="OBSID",
    )
    ra_deg = django_filters.RangeFilter(
        field_name="ra_deg",
        label="RA (degrees)",
        widget=django_filters.widgets.RangeWidget(),
    )
    dec_deg = django_filters.RangeFilter(field_name="dec_deg", label="DEC (degrees)")
    can_fluence = django_filters.RangeFilter(
        field_name="can_fluence", label="Fluence (Jy.s)"
    )

    class Meta:
        model = Candidate
        fields = []
