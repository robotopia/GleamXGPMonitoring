from django.contrib import admin
from .models import Observation, Filter, Candidate, Rating

admin.site.register(Observation)
admin.site.register(Filter)
admin.site.register(Candidate)
admin.site.register(Rating)
