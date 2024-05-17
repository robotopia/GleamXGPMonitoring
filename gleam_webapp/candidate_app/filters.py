import django_filters
from .models import Candidate


class CandidateFilter(django_filters.FilterSet):
    class Meta:
        model = Candidate
        fields = {
            "id": ["lt", "gt"],
            "ra_hms": ["lt", "gt"],
            "dec_dms": ["lt", "gt"],
            "obs_id": ["lt", "gt"],
            "can_fluence": ["lt", "gt"],
        }
