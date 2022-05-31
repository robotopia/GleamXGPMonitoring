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
    cent_freq = models.FloatField(blank=True, null=True, verbose_name="Centre Frequency (MHz)")
    freq_res = models.IntegerField(blank=True, null=True, verbose_name="Frequency Resolution (KHz)")
    int_time = models.FloatField(blank=True, null=True, verbose_name="Integration Time (s)")

class Filter(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(verbose_name="Short Name", max_length=64, blank=True, null=True)
    description = models.CharField(verbose_name="Description", max_length=256, blank=True, null=True)

class Candidate(models.Model):
    id = models.AutoField(primary_key=True)
    obs_id = models.ForeignKey(
        Observation,
        on_delete=models.CASCADE,
        related_name="candidate",
        verbose_name="Observation ID in GPS time",
    )
    filter_id = models.ForeignKey(
        Filter,
        on_delete=models.CASCADE,
        related_name="candidate",
    )
    png_path = models.FileField(upload_to="candidates/", max_length=1024, null=True)
    gif_path = models.FileField(upload_to="candidates/", max_length=1024, null=True)
    notes = models.TextField(blank=True, null=True, default="")

    # Data in the fits file
    can_x_pix = models.FloatField(blank=True, null=True, verbose_name="Candidate x pixel coordinate in obsevration")
    can_y_pix = models.FloatField(blank=True, null=True, verbose_name="Candidate y pixel coordinate in obsevration")
    can_ra_deg = models.FloatField(blank=True, null=True, verbose_name="Candidate Right Acension (deg)")
    can_dec_deg = models.FloatField(blank=True, null=True, verbose_name="Candidate Declination (deg)")
    can_cent_sep_deg = models.FloatField(blank=True, null=True, verbose_name="Candidate seperation from observation central pointing (deg)")
    can_rad_pix = models.FloatField(blank=True, null=True, verbose_name="Candidate radius in pixels")
    can_rad_deg = models.FloatField(blank=True, null=True, verbose_name="Candidate radius in degrees")
    can_peak_flux = models.FloatField(blank=True, null=True, verbose_name="Candidate peak flux in Jy")
    can_fluence = models.FloatField(blank=True, null=True, verbose_name="Candidate fluence in Jy s")
    can_beam = models.FloatField(blank=True, null=True, verbose_name="Primary beam value at the candidate location")
    can_det_stat = models.FloatField(blank=True, null=True, verbose_name="Candidate detection statistic - arbitrary value returned by filter")
    can_mod_ind = models.IntegerField(blank=True, null=True, verbose_name="Candidate modulation index")
    nks_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="Nearest known source name")
    nks_x_pix = models.FloatField(blank=True, null=True, verbose_name="Nearest known source x pixel coordinate in observation")
    nks_y_pix = models.FloatField(blank=True, null=True, verbose_name="Nearest known source y pixel coordinate in observation")
    nks_ra_deg = models.FloatField(blank=True, null=True, verbose_name="Nearest known source Right Acension (deg)")
    nks_dec_deg = models.FloatField(blank=True, null=True, verbose_name="Nearest known source Declination (deg)")
    nks_flux = models.FloatField(blank=True, null=True, verbose_name="Nearest known source integrated flux density in Jy")
    nks_res = models.FloatField(blank=True, null=True, verbose_name="")
    nks_res_dif = models.FloatField(blank=True, null=True, verbose_name="Nearest known source number of stds above mean residual")
    nks_det_stat = models.FloatField(blank=True, null=True, verbose_name="Nearest known source detection statistic - arbitrary value returned by filter")
    can_nks_sep_pix = models.FloatField(blank=True, null=True, verbose_name="Separation between candidate and known in pixels")
    can_nks_sep_deg = models.FloatField(blank=True, null=True, verbose_name="Separation between candidate and known in degrees")
    can_nks_flux_rat = models.FloatField(blank=True, null=True, verbose_name="Ratio of candidate and known flux")
    can_nks_is_close = models.BooleanField(null=True, verbose_name="")

    # Coordinates converted to hms/dms
    can_ra_hms  = models.CharField(max_length=32, blank=True, null=True, verbose_name="Candidate Right Acension (HH:MM:SS)")
    can_dec_dms = models.CharField(max_length=32, blank=True, null=True, verbose_name="Candidate Declination (DD:MM:SS)")
    nks_ra_hms  = models.CharField(max_length=32, blank=True, null=True, verbose_name="Nearest known source Right Acension (HH:MM:SS)")
    nks_dec_dms = models.CharField(max_length=32, blank=True, null=True, verbose_name="Nearest known source Declination (DD:MM:SS)")



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
    T = 'T'
    A = 'A'
    RFI = 'RFI'
    SL = 'SL'
    CAND_TYPE_CHOICES = (
        (T,   'Transient'),
        (A,   'Airplane'),
        (RFI, 'RFI'),
        (SL,  'Sidelobe'),
    )
    cand_type = models.CharField(max_length=3, choices=CAND_TYPE_CHOICES, null=True)