import django_tables2 as tables
from .models import Candidate
from django.utils.html import format_html


class ImageColumn(tables.Column):
    def render(self, value):
        return format_html('<img src="/media/{}" width="250" height="250"/>', value)


class CandidateTable(tables.Table):
    id = tables.LinkColumn(
        "candidate_rating",
        args=[tables.A("pk")],
    )
    rating_count = tables.Column()
    png_path = ImageColumn(verbose_name="Preview", orderable=False)
    ra_hms = tables.Column(order_by=("ra_deg",), verbose_name="RA")
    dec_dms = tables.Column(order_by=("dec_deg",), verbose_name="DEC")
    obs_id = tables.Column(verbose_name="OBSID")
    can_fluence = tables.Column(verbose_name="Fluence (Jy.s)")
    can_det_stat = tables.Column(verbose_name="Detection Stat")
    metadata_link = tables.LinkColumn(
        "candidate_metadata",
        text=lambda record: "View Meta" if hasattr(record, "metadata") else "",
        args=[tables.A("pk")],
        verbose_name="Metadata",
        orderable=False,
    )

    sep = tables.Column(verbose_name="Sep")

    class Meta:
        model = Candidate
        attrs = {
            "class": "table table-hover table-striped",
            "thead": {"class": "table-secondary"},
        }
        template_name = "candidate_app/table.html"
        fields = (
            "id",
            "rating_count",
            "notes",
            "ra_hms",
            "dec_dms",
            "obs_id",
            "can_fluence",
            "can_det_stat",
            "png_path",
            "metadata_link",
        )
