from django.db import models
from django.conf import settings

from datetime import datetime


class Observation(models.Model):
    observation_id = models.BigIntegerField(primary_key=True)
    obsname = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Obs name"
    )
    starttime = models.BigIntegerField(verbose_name="Start Time (GPS sec)")
    stoptime = models.BigIntegerField(verbose_name="Stop Time (GPS sec)")
    ra_tile_dec = models.FloatField(blank=True, null=True, verbose_name="RA (deg)")
    dec_tile_dec = models.FloatField(blank=True, null=True, verbose_name="Dec (deg)")
    ra_tile_hms = models.CharField(
        max_length=32, blank=True, null=True, verbose_name="RA (HH:MM:SS)"
    )
    dec_tile_dms = models.CharField(
        max_length=32, blank=True, null=True, verbose_name="Dec (DD:MM:SS)"
    )
    projectid = models.CharField(max_length=16, blank=True, null=True)
    azimuth = models.FloatField(blank=True, null=True, verbose_name="Azimuth (deg)")
    elevation = models.FloatField(blank=True, null=True, verbose_name="Elevation (deg)")
    frequency_channels = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name="Frequency Channels (x1.28 MHz)",
    )
    cent_freq = models.FloatField(
        blank=True, null=True, verbose_name="Centre Frequency (MHz)"
    )
    freq_res = models.IntegerField(
        blank=True, null=True, verbose_name="Frequency Resolution (KHz)"
    )
    int_time = models.FloatField(
        blank=True, null=True, verbose_name="Integration Time (s)"
    )

    def __str__(self):
        return f"{self.observation_id}"


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        verbose_name="Project name", max_length=64, blank=True, null=True
    )

    def __str__(self):
        return f"{self.name}"


class Filter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        verbose_name="Short Name", max_length=64, blank=True, null=True
    )
    description = models.CharField(
        verbose_name="Description", max_length=256, blank=True, null=True
    )

    def __str__(self):
        return f"{self.name}"


class Candidate(models.Model):
    id = models.AutoField(primary_key=True)
    obs_id = models.ForeignKey(
        Observation,
        on_delete=models.CASCADE,
        related_name="candidate",
        verbose_name="Observation ID in GPS time",
    )
    filter = models.ForeignKey(
        Filter,
        on_delete=models.CASCADE,
        related_name="candidate",
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="candidate"
    )

    png_path = models.FileField(upload_to="candidates/", max_length=1024, null=True)
    gif_path = models.FileField(upload_to="candidates/", max_length=1024, null=True)
    notes = models.TextField(blank=True, null=True, default="")

    # Data in the fits file
    x_pix = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Candidate island central x pixel coordinate",
    )
    y_pix = models.FloatField(
        blank=True, null=True, verbose_name="Candidate island central pixel coordinate"
    )
    ra_deg = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Candidate island central Right Acension (deg)",
    )
    dec_deg = models.FloatField(
        blank=True, null=True, verbose_name="Candidate island central Declination (deg)"
    )
    cent_sep_deg = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Candidate seperation from observation central pointing (deg)",
    )
    rad_pix = models.FloatField(
        blank=True, null=True, verbose_name="Candidate island radius in pixels"
    )
    rad_deg = models.FloatField(
        blank=True, null=True, verbose_name="Candidate island radius in degrees"
    )
    area_pix = models.FloatField(
        blank=True, null=True, verbose_name="Candidate island area in pixels^2"
    )
    can_peak_flux = models.FloatField(
        blank=True, null=True, verbose_name="Candidate peak flux in Jy"
    )
    can_fluence = models.FloatField(
        blank=True, null=True, verbose_name="Candidate fluence in Jy s"
    )
    can_beam = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Primary beam value at the candidate location",
    )
    can_det_stat = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Candidate detection statistic - arbitrary value returned by filter",
    )
    can_mod_ind = models.IntegerField(
        blank=True, null=True, verbose_name="Candidate modulation index"
    )
    nks_name = models.CharField(
        max_length=64, blank=True, null=True, verbose_name="Nearest known source name"
    )
    nks_x_pix = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Nearest known source x pixel coordinate in observation",
    )
    nks_y_pix = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Nearest known source y pixel coordinate in observation",
    )
    nks_ra_deg = models.FloatField(
        blank=True, null=True, verbose_name="Nearest known source Right Acension (deg)"
    )
    nks_dec_deg = models.FloatField(
        blank=True, null=True, verbose_name="Nearest known source Declination (deg)"
    )
    nks_flux = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Nearest known source integrated flux density in Jy",
    )
    nks_res = models.FloatField(blank=True, null=True, verbose_name="")
    nks_res_dif = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Nearest known source number of stds above mean residual",
    )
    nks_det_stat = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Nearest known source detection statistic "
        "- arbitrary value returned by filter",
    )
    nks_sep_pix = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Separation between candidate and known in pixels",
    )
    nks_sep_deg = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Separation between candidate and known in degrees",
    )
    can_nks_flux_rat = models.FloatField(
        blank=True, null=True, verbose_name="Ratio of candidate and known flux"
    )
    can_nks_is_close = models.BooleanField(null=True, verbose_name="")

    # Coordinates converted to hms/dms
    ra_hms = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name="Candidate Right Acension (HH:MM:SS)",
    )
    dec_dms = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name="Candidate Declination (DD:MM:SS)",
    )
    nks_ra_hms = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name="Nearest known source Right Acension (HH:MM:SS)",
    )
    nks_dec_dms = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name="Nearest known source Declination (DD:MM:SS)",
    )

    # def __str__(self):
    #     return f"{self.id}_obs{self.obs_id.observation_id}_{self.filter.name}"


T = "T"
AP = "AP"
RFI = "RFI"
SL = "SL"
A = "A"
CC = "CC"
S = "S"
P = "P"
AGN = "AGN"
D = "D"
BF = "BF"
O = "O"  # noqa: E741
CAND_TYPE_CHOICES = (
    (T, "Transient"),
    (AP, "Airplane"),
    (RFI, "RFI"),
    (SL, "Sidelobe"),
    (A, "Alias"),
    (CC, "CHG Centre"),
    (S, "Scintillation"),
    (P, "Pulsar"),
    (AGN, "AGN"),
    (D, "Drift"),
    (BF, "Bad Frame"),
    (O, "Other"),
)


class Rating(models.Model):
    id = models.AutoField(primary_key=True)
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="rating",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rating",
    )
    rating = models.IntegerField(blank=True, null=True)
    cand_type = models.CharField(max_length=3, choices=CAND_TYPE_CHOICES, null=True)
    date = models.DateTimeField(default=datetime.now, blank=True)


class xml_ivorns(models.Model):
    id = models.AutoField(primary_key=True)
    ivorn = models.CharField(max_length=128, unique=True)
