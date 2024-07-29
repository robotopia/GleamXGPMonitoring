from django.contrib import admin
from .models import (
    Observation,
    Filter,
    Candidate,
    Rating,
    Project,
    Classification,
    Metadata,
    ATNFPulsar,
    Association,
)


class CandidateAdmin(admin.ModelAdmin):
    search_help_text = "Filter by observation ID"
    search_fields = ["obs_id__observation_id"]
    list_filter = ("obs_id",)
    list_display = ("id", "obs_id", "filter")
    model = Candidate


class PulsarAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "raj", "decj")
    model = ATNFPulsar


admin.site.register(Observation)
admin.site.register(Filter)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Metadata)
admin.site.register(Rating)
admin.site.register(Project)
admin.site.register(Classification)
admin.site.register(Association)
admin.site.register(ATNFPulsar, PulsarAdmin)
