import django_tables2 as tables
from .models import Candidate
from django.utils.html import format_html


class ImageColumn(tables.Column):
    def render(self, value):
        return format_html('<img src="{}" width="100" height="100"/>', value)


class CandidateTable(tables.Table):
    rating_count = tables.Column()
    png_path = ImageColumn()
    ra_hms = tables.Column(order_by=("ra_deg",))
    dec_dms = tables.Column(order_by=("dec_deg",))

    class Meta:
        model = Candidate
        template_name = "django_tables2/bootstrap.html"
        fields = (
            "id",
            "rating_count",
            "notes",
            "ra_hms",
            "dec_dms",
            "obs_id",
            "png_path",
        )
        order_by = ("id",)
