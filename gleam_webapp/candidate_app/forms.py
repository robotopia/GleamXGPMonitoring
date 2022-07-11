from django import forms
from . import models

# Add a default to candidate type choices
CAND_TYPE_CHOICES = models.CAND_TYPE_CHOICES
N = 'None'
CAND_TYPE_CHOICES += ((N,   'All columns'),)

ORDER_BY_CHOICES = (
    ('id','ID'),
    ('avg_rating', 'Rating'),
    ('num_ratings', 'Count'),
    ('notes', 'Notes'),
    ('transient_count', 'N Tranisent'),
    ('airplane_count', 'N Airplane'),
    ('rfi_count', 'N RFI'),
    ('sidelobe_count', 'N Sidelobe'),
    ('alias_count', 'N Alias'),
    ('chgcentre_count', 'N CHG Center'),
    ('scintillation_count', 'N Scintillation'),
    ('pulsar_count', 'N Pulsar'),
    ('other_count', 'N Other'),
    ('ra_hms', 'RA'),
    ('dec_dms', 'Dec'),
    ('obs_id', 'Obs ID'),
)

ASC_DEC_CHOICES = (
    ('', 'Ascending'),
    ('-', 'Decending')
)

class CanidateFilterForm(forms.Form):
    rating_cutoff = forms.FloatField(required=False)
    observation_id = forms.ModelChoiceField(models.Observation.objects.all(), empty_label="All observations", required=False)
    column_display = forms.ChoiceField(choices=CAND_TYPE_CHOICES, required=False, initial='None')
    order_by = forms.ChoiceField(choices=ORDER_BY_CHOICES, required=False, initial='avg_rating')
    asc_dec = forms.ChoiceField(choices=ASC_DEC_CHOICES, required=False, initial='-')
