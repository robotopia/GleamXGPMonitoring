from django.contrib import admin
from .models import Observation, Filter, Candidate

admin.site.register(Observation)
admin.site.register(Filter)
admin.site.register(Candidate)
