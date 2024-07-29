from django import forms
from django.core.exceptions import ValidationError
from . import models


SESSION_ORDER_CHOICES = (
    ("rand", "Random"),
    ("new", "Newest"),
    ("old", "Oldest"),
    ("brig", "Brightest"),
    ("faint", "Faintest"),
)

SESSION_FILTER_CHOICES = (
    ("unrank", "Unranked Candidates"),
    ("old", "Candidates Not Ranked Recently"),
    ("all", "All Candidates"),
)


class SessionSettingsForm(forms.Form):
    ordering = forms.ChoiceField(
        choices=SESSION_ORDER_CHOICES, required=False, initial="rand"
    )
    filtering = forms.ChoiceField(
        choices=SESSION_FILTER_CHOICES, required=False, initial="unrank"
    )
    exclude_87 = forms.BooleanField(required=False)
    exclude_118 = forms.BooleanField(required=False)
    exclude_154 = forms.BooleanField(required=False)
    exclude_184 = forms.BooleanField(required=False)
    exclude_200 = forms.BooleanField(required=False)
    exclude_215 = forms.BooleanField(required=False)

    project = forms.ModelChoiceField(
        queryset=models.Project.objects.all(), to_field_name="name", empty_label=None
    )

    def clean(self):
        cleaned_data = super().clean()
        # replace the project object with it's name
        # since the project object will cause a "Not JSon serializable" error
        cleaned_data["project"] = cleaned_data["project"].name
        if (
            cleaned_data.get("filtering") == "all"
            and cleaned_data.get("ordering") != "rand"
        ):
            raise ValidationError(
                "ERROR: You can not order all candidates by anything other than"
                "random as it will always give you the same candidate. "
                "Please either order randomly or filter by candidates not "
                "ranked recently."
            )
