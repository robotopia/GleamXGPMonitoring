from django.db import models
from django.conf import settings

class Observation(models.Model):
    observation_id = models.BigIntegerField(primary_key=True)
    obsname = models.CharField(max_length=128, blank=True, null=True, verbose_name="Obs name")
    starttime = models.BigIntegerField(verbose_name="Start Time (GPS sec)")
    stoptime = models.BigIntegerField(verbose_name="Stop Time (GPS sec)")
    ra_tile_dec = models.FloatField(blank=True, null=True, verbose_name="RA (deg)")
    dec_tile_dec= models.FloatField(blank=True, null=True, verbose_name="Dec (deg)")
    ra_tile_hms = models.CharField(max_length=32, blank=True, null=True, verbose_name="RA (HH:MM:SS)")
    dec_tile_dms= models.CharField(max_length=32, blank=True, null=True, verbose_name="Dec (DD:MM:SS)")
    projectid = models.CharField(max_length=16, blank=True, null=True)
    azimuth = models.FloatField(blank=True, null=True, verbose_name="Azimuth (deg)")
    elevation = models.FloatField(blank=True, null=True, verbose_name="Elevation (deg)")
    frequency_channels = models.CharField(max_length=128, blank=True, null=True, verbose_name="Frequency Channels (x1.28 MHz)")
    freq_res = models.IntegerField(blank=True, null=True, verbose_name="Frequency Resolution (KHz)")
    int_time = models.FloatField(blank=True, null=True, verbose_name="Integration Time (s)")

class Filter(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(verbose_name="Short Name", max_length=64, blank=True, null=True)
    description = models.CharField(verbose_name="Description", max_length=256, blank=True, null=True)

class Candidate(models.Model):
    id = models.BigIntegerField(primary_key=True)
    candidate = models.ForeignKey(
        Observation,
        on_delete=models.CASCADE,
        related_name="candidate",
    )
    candidate = models.ForeignKey(
        Filter,
        on_delete=models.CASCADE,
        related_name="candidate",
    )
    png_path = models.FileField(upload_to="candidates/", max_length=1024, null=True)
    ra_dec = models.FloatField(blank=True, null=True, verbose_name="RA (deg)")
    dec_dec= models.FloatField(blank=True, null=True, verbose_name="Dec (deg)")
    ra_hms = models.CharField(max_length=32, blank=True, null=True, verbose_name="RA (HH:MM:SS)")
    dec_dms= models.CharField(max_length=32, blank=True, null=True, verbose_name="Dec (DD:MM:SS)")
    flux = models.FloatField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True, default="")


class Ratings(models.Model):
    id = models.BigIntegerField(primary_key=True)
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    rating = models.IntegerField(blank=True, null=True)
    rfi = models.BooleanField(blank=True)