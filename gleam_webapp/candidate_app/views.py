# from mwa_trigger.parse_xml import parsed_VOEvent
import csv
import json
import logging
import random
from datetime import datetime, timedelta

import voeventdb.remote.apiv1 as apiv1
import voeventparse
from astropy import units
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astroquery.simbad import Simbad
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Q, F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django_q3c.expressions import Q3CRadialQuery, Q3CDist
from django_tables2 import SingleTableView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import download_fits

# from voeventdb.remote.apiv1 import FilterKeys, OrderValues

from . import forms, models, serializers, tables, filters

logger = logging.getLogger(__name__)


class FilteredCandidateQuerysetMixin:

    def get_filtered_queryset(self):
        queryset = models.Candidate.objects.all()

        session_settings = self.request.session.get("session_settings", None)
        if session_settings:
            queryset = queryset.filter(project__name=session_settings["project"])

        queryset = queryset.annotate(rating_count=Count("rating"))

        self.filterset = filters.CandidateFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs


class CandidateListView(FilteredCandidateQuerysetMixin, SingleTableView):
    model = models.Candidate
    table_class = tables.CandidateTable
    template_name = "candidate_app/candidate_list.html"
    paginate_by = 15

    def get_queryset(self):
        return self.get_filtered_queryset()

    def get_context_data(self, **kwargs):
        session_settings = self.request.session.get("session_settings", 0)

        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        if session_settings:
            context["project_name"] = session_settings["project"]
        else:
            context["project_name"] = "all projects"
        return context


class CandidateFITSExportView(FilteredCandidateQuerysetMixin, SingleTableView):
    def get(self, request, *args, **kwargs):
        # Get the filtered queryset
        filtered_qs = self.get_filtered_queryset()
        # Download fits
        response = download_fits(request, filtered_qs, "Candidates")
        return response


def home_page(request):
    return render(request, "candidate_app/home_page.html")


def cone_search_simbad(request):  # , ra_deg, dec_deg, dist_arcmin):
    ra_deg = 0
    dec_deg = 0
    dist_arcmin = 2
    if request.method == "POST":
        data = json.loads(request.body.decode())
        ra_deg = data.get("ra_deg", 0)
        dec_deg = data.get("dec_deg", 0)
        dist_arcmin = float(data.get("dist_arcmin", 1))

    # limit query distance or we get very long timeouts
    dist_arcmin = min(dist_arcmin, 60)

    coord = SkyCoord(ra_deg, dec_deg, unit=(units.deg, units.deg), frame="icrs")
    # Perform simbad query
    raw_result_table = Simbad.query_region(coord, radius=dist_arcmin * units.arcmin)
    simbad_result_table = []
    # Reformat the result into the format we want
    if raw_result_table:
        for result in raw_result_table:
            search_term = result["MAIN_ID"].replace("+", "%2B").replace(" ", "+")
            simbad_coord = SkyCoord(
                result["RA"], result["DEC"], unit=(units.hour, units.deg), frame="icrs"
            )
            ra = simbad_coord.ra.to_string(unit=units.hour, sep=":")[:11]
            dec = simbad_coord.dec.to_string(unit=units.deg, sep=":")[:11]
            sep = coord.separation(simbad_coord).arcminute
            simbad_result_table.append(
                {
                    "name": result["MAIN_ID"],
                    "search_term": search_term,
                    "ra": ra,
                    "dec": dec,
                    "sep": sep,
                }
            )
    return render(
        request,
        "candidate_app/simbad_table.html",
        context={"simbad_result_table": simbad_result_table},
    )


def cone_search(request):
    if request.method == "POST":
        data = json.loads(request.body.decode())
        ra_deg = data.get("ra_deg", 0)
        dec_deg = data.get("dec_deg", 0)
        dist_arcmin = data.get("dist_arcmin", 1)
        exclude = data.get("exclude_id", None)
        project = data.get("project", None)

        # Find nearby candidates
        table = models.Candidate.objects

        # Restrict project if given
        if project:
            table = table.filter(project__name=project)

        # if we are given a candidate ID then exclude it from the results
        if exclude:
            table = table.exclude(id=exclude)

        table = (
            table.filter(
                Q(
                    Q3CRadialQuery(
                        center_ra=ra_deg,
                        center_dec=dec_deg,
                        ra_col="ra_deg",
                        dec_col="dec_deg",
                        radius=float(dist_arcmin) / 60.0,
                    )
                )
            )
            .annotate(  # do the distance calcs in the db
                sep=Q3CDist(
                    ra1=F("ra_deg"),
                    dec1=F("dec_deg"),
                    ra2=ra_deg,
                    dec2=dec_deg,
                )
                * 60  # arcsec -> degrees
            )
            .order_by("sep")
        )

        table = table.values()
    else:
        table = []
    return render(
        request,
        "candidate_app/cone_search_table.html",
        context={"table": table},
    )


def cone_search_pulsars(request):
    if request.method == "POST":
        data = json.loads(request.body.decode())
        print(data)
        ra_deg = float(data.get("ra_deg", 0))
        dec_deg = float(data.get("dec_deg", 0))
        dist_arcmin = float(data.get("dist_arcmin", 1))
        # Perform atnf query
        table = (
            models.ATNFPulsar.objects.filter(
                Q(
                    Q3CRadialQuery(
                        center_ra=ra_deg,
                        center_dec=dec_deg,
                        ra_col="raj",
                        dec_col="decj",
                        radius=dist_arcmin / 60.0,
                    )
                )
            )
            .annotate(  # do the distance calcs in the db
                sep=Q3CDist(
                    ra1=F("raj"),
                    dec1=F("decj"),
                    ra2=ra_deg,
                    dec2=dec_deg,
                )
                * 60  # arcsec -> degrees
            )
            .order_by("sep")
            .values()
        )

    else:
        table = []

    return render(
        request,
        "candidate_app/atnf_pulsar_table.html",
        context={"table": table},
    )


@login_required
def candidate_rating(request, id, arcmin=2):
    candidate = get_object_or_404(models.Candidate, id=id)

    # Convert time to readable format
    time = Time(
        Time(candidate.obs_id.starttime, format="gps"), format="iso", scale="utc"
    )

    # Grab any previous ratings
    u = request.user
    rating = models.Rating.objects.filter(candidate=candidate, user=u).first()

    # Convert seperation to arcminutes
    if candidate.nks_sep_deg is None:
        sep_arcmin = None
    else:
        sep_arcmin = candidate.nks_sep_deg * 60

    # Perform voevent database query
    # https://voeventdbremote.readthedocs.io/en/latest/notebooks/00_quickstart.html
    # conesearch skycoord and angle error
    # cand_err = Angle(arcmin, unit=units.arcmin)
    # cand_err = Angle(5,  unit=units.deg)
    # cone = (cand_coord, cand_err)

    # my_filters = {
    #     FilterKeys.role: "observation",
    #     FilterKeys.authored_since: time.tt.datetime - timedelta(hours=1),
    #     FilterKeys.authored_until: time.tt.datetime + timedelta(hours=1),
    #     # FilterKeys.authored_since: time.tt.datetime - timedelta(days=1),
    #     # FilterKeys.authored_until: time.tt.datetime + timedelta(days=1),
    #     FilterKeys.cone: cone,
    # }
    voevents = []

    context = {
        "candidate": candidate,
        "rating": rating,
        "time": time,
        "sep_arcmin": sep_arcmin,
        "arcmin_search": arcmin,
        "cand_type_choices": tuple(
            (c.name, c.name) for c in models.Classification.objects.all()
        ),
        "voevents": voevents,
    }
    return render(request, "candidate_app/candidate_rating_form.html", context)


def voevent_view(request, id):
    ivorn = models.xml_ivorns.objects.filter(id=id).first().ivorn
    xml_packet = apiv1.packet_xml(ivorn)
    v = voeventparse.loads(xml_packet)
    xml_pretty_str = voeventparse.prettystr(v)
    return HttpResponse(xml_pretty_str, content_type="text/xml")


@login_required
def token_manage(request):
    u = request.user
    token = Token.objects.filter(user=u).first()
    return render(request, "candidate_app/token_manage.html", {"token": token})


@login_required
def token_create(request):
    u = request.user
    token = Token.objects.filter(user=u)
    if token.exists():
        token.delete()
    Token.objects.create(user=u)
    return redirect(reverse("token_manage"))


@login_required
@api_view(["POST"])
@transaction.atomic
def candidate_update_rating(request, id):
    candidate = models.Candidate.objects.filter(id=id).first()
    if candidate is None:
        raise ValueError("Candidate not found")

    rating = models.Rating.objects.filter(
        candidate=candidate, user=request.user
    ).first()
    if rating is None:
        # User hasn't made a rating of this cand so make one
        rating = models.Rating(
            candidate=candidate,
            user=request.user,
            rating=None,
        )

    classification = request.data.get("classification", None)
    if classification:
        rating.classification = models.Classification.objects.filter(
            name=classification
        ).first()

    score = request.data.get("rating", None)
    if score:
        logger.debug("setting score %s=>%s", rating.rating, score)
        rating.rating = score

    # Update time
    rating.date = datetime.now(tz=timezone.utc)

    rating.save()

    # Update candidate notes
    notes = request.data.get("notes", "")
    if candidate.notes != notes:
        logger.debug("setting notes %s=>%s", candidate.notes, notes)
        candidate.notes = notes
    candidate.save()

    # Redirects to a random next candidate
    return redirect(reverse("candidate_random"))


@login_required
@api_view(["POST"])
@transaction.atomic
def candidate_update_catalogue_query(request, id):
    logger.debug(request.data)
    candidate = models.Candidate.objects.filter(id=id).first()
    if candidate is None:
        raise ValueError("Candidate not found")
    logger.debug("candidate obj %s", candidate)

    arcmin = request.data.get("arcmin", None)
    if arcmin:
        logger.debug(f"New query with {arcmin}")
        return candidate_rating(request, id, arcmin=arcmin)


@login_required
def candidate_random(request):
    # Get session data for candidate ordering and inclusion settings
    session_settings = request.session.get("session_settings", 0)

    # deal with users who have no session settings
    if not session_settings:
        return render(request, "candidate_app/nothing_to_rate.html")

    user = request.user
    # choose all the candidates this user hasn't rated
    next_cands = models.Candidate.objects.exclude(rating__user=user)

    # filter based on selected project
    next_cands = next_cands.filter(project__name=session_settings["project"])

    # Filter candidates based on ranking
    if session_settings["filtering"] == "unrank":
        # Get unrated candidates
        next_cands = next_cands.filter(rating__isnull=True)
        if not next_cands.exists():
            return render(
                request,
                "candidate_app/nothing_to_rate.html",
                {"project": session_settings["project"]},
            )
    elif session_settings["filtering"] == "old":
        # Get candidates the user hasn't recently ranked
        next_cands = next_cands.exclude(
            rating__date__gte=datetime.now() - timedelta(days=7)
        )
        if not next_cands.exists():
            return render(
                request,
                "candidate_app/nothing_to_rate.html",
                {"project": session_settings["project"]},
            )

    # Filter based on observation frequencies (+/- 1 MHz)
    if session_settings["exclude_87"]:
        next_cands = next_cands.exclude(
            obs_id__cent_freq__lt=87.68 + 1, obs_id__cent_freq__gt=87.68 - 1
        )
    if session_settings["exclude_118"]:
        next_cands = next_cands.exclude(
            obs_id__cent_freq__lt=118.50 + 1, obs_id__cent_freq__gt=118.50 - 1
        )
    if session_settings["exclude_154"]:
        next_cands = next_cands.exclude(
            obs_id__cent_freq__lt=154.24 + 1, obs_id__cent_freq__gt=154.24 - 1
        )
    if session_settings["exclude_184"]:
        next_cands = next_cands.exclude(
            obs_id__cent_freq__lt=184.96 + 1, obs_id__cent_freq__gt=184.96 - 1
        )
    if session_settings["exclude_200"]:
        next_cands = next_cands.exclude(
            obs_id__cent_freq__lt=200.32 + 1, obs_id__cent_freq__gt=200.32 - 1
        )
    if session_settings["exclude_215"]:
        next_cands = next_cands.exclude(
            obs_id__cent_freq__lt=215.68 + 1, obs_id__cent_freq__gt=215.68 - 1
        )

    # Use session data to decide candidate order
    if session_settings["ordering"] == "rand":
        candidate = random.choice(list(next_cands))
    elif session_settings["ordering"] == "new":
        candidate = next_cands.order_by("-obs_id__starttime").first()
    elif session_settings["ordering"] == "old":
        candidate = next_cands.order_by("obs_id__starttime").first()
    elif session_settings["ordering"] == "brig":
        candidate = next_cands.order_by("-can_peak_flux").first()
    elif session_settings["ordering"] == "faint":
        candidate = next_cands.order_by("can_peak_flux").first()
    return redirect(reverse("candidate_rating", args=(candidate.id,)))


def session_settings(request):
    # Get session data to keep filters when changing page
    session_settings = request.session.get("session_settings", 0)
    # print(session_settings)

    # Check filter form
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = forms.SessionSettingsForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            cleaned_data = {**form.cleaned_data}
            request.session["session_settings"] = cleaned_data
            # print("here", cleaned_data)
    else:
        if session_settings != 0:
            # Prefil form with previous session results
            form = forms.SessionSettingsForm(
                initial=session_settings,
            )
        else:
            form = forms.SessionSettingsForm()
    context = {
        "form": form,
        "order_choices": form.fields["ordering"].choices,
        "filter_choices": form.fields["filtering"].choices,
        "project_choices": form.fields["project"].choices,
    }

    return render(request, "candidate_app/session_settings.html", context)


@api_view(["POST"])
@transaction.atomic
def observation_create(request):
    obs = serializers.ObservationSerializer(data=request.data)
    if models.Observation.objects.filter(
        observation_id=request.data["observation_id"]
    ).exists():
        return Response(
            "Observation already created so skipping", status=status.HTTP_201_CREATED
        )
    if obs.is_valid():
        obs.save()
        return Response(obs.data, status=status.HTTP_201_CREATED)
    logger.debug(request.data)
    return Response(obs.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@transaction.atomic
def candidate_create(request):
    # Get or create filter
    filter_name = request.data.get("filter_id")
    if models.Filter.objects.filter(name=filter_name).exists():
        filter = models.Filter.objects.filter(name=filter_name).first()
    else:
        filter = models.Filter.objects.create(name=filter_name)
    request.data["filter"] = filter.id

    cand = serializers.CandidateSerializer(data=request.data)
    png_file = request.data.get("png")
    gif_file = request.data.get("gif")
    if cand.is_valid():
        # Find obsid
        # obs = models.Observation.objects.filter(observation_id=obsid).first()
        if png_file is None:
            return Response("Missing png file", status=status.HTTP_400_BAD_REQUEST)
        if gif_file is None:
            return Response("Missing gif file", status=status.HTTP_400_BAD_REQUEST)
        cand.save(png_path=png_file, gif_path=gif_file, filter=filter)
        return Response(cand.data, status=status.HTTP_201_CREATED)
    logger.debug(request.data)
    logger.error(cand.errors)
    return Response(cand.errors, status=status.HTTP_400_BAD_REQUEST)


def survey_status(request):
    # Order by the column the user clicked or by observation_id by default
    order_by = request.GET.get("order_by", "observation_id")
    obs_list = (
        models.Observation.objects.all()
        .annotate(
            candidates=Count("candidate"),
            rated_candidates=Count(
                "candidate", filter=Q(candidate__rating__isnull=False)
            ),
        )
        .order_by(order_by)
    )
    context = {"obs": obs_list}
    return render(request, "candidate_app/survey_status.html", context)


def download_csv(request, queryset, table):
    if not request.user.is_staff:
        raise PermissionDenied
    opts = queryset.model._meta
    response = HttpResponse(content_type="text/csv")
    # force download.
    response["Content-Disposition"] = f'attachment; filename="{table}.csv"'
    # the csv writer
    writer = csv.writer(response)
    field_names = [field.name for field in opts.fields]
    # Write a first row with header information
    writer.writerow(field_names)
    # Write data rows
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response


def download_data(request, table):
    if table == "user":
        from django.contrib.auth import get_user_model

        this_model = get_user_model()
    elif table == "rating":
        this_model = models.Rating
    elif table == "candidate":
        this_model = models.Candidate
    elif table == "observation":
        this_model = models.Observation
    elif table == "filter":
        this_model = models.Filter
    response = download_fits(request, this_model.objects.all(), table)
    # response = download_csv(request, this_model.objects.all(), table)
    return response
