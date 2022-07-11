from django.shortcuts import render
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count, Q, Avg
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token

import random
import psrqpy
from datetime import datetime, timedelta
from mwa_trigger.parse_xml import parsed_VOEvent

from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy import units
from astropy.coordinates import Angle
from astroquery.simbad import Simbad

import voeventdb.remote.apiv1 as apiv1
from voeventdb.remote.apiv1 import FilterKeys, OrderValues
import voeventparse

from . import models, serializers, forms

import logging
logger = logging.getLogger(__name__)

def home_page(request):
    return render(request, 'candidate_app/home_page.html')


@login_required
def candidate_rating(request, id, arcmin=2):
    candidate = get_object_or_404(models.Candidate, id=id)

    # Convert time to readable format
    time = Time(Time(candidate.obs_id.starttime, format='gps'), format='iso', scale='utc')

    # Grab any previous ratings
    u = request.user
    rating = models.Rating.objects.filter(candidate=candidate, user=u).first()

    # Convert seperation to arcminutes
    if candidate.nks_sep_deg is None:
        sep_arcmin = None
    else:
        sep_arcmin = candidate.nks_sep_deg * 60

    cand_coord = SkyCoord(candidate.ra_deg, candidate.dec_deg, unit=(units.deg, units.deg), frame='icrs')

    # Perform simbad query
    raw_result_table = Simbad.query_region(cand_coord, radius=float(arcmin) * units.arcmin)
    simbad_result_table = []
    # Reformat the result into the format we want
    if raw_result_table is not None:
        for result in raw_result_table:
            search_term = result["MAIN_ID"].replace("+", "%2B").replace(" ", "+")
            simbad_coord = SkyCoord(result["RA"], result["DEC"], unit=(units.hour, units.deg), frame='icrs')
            ra  = simbad_coord.ra.to_string(unit=units.hour, sep=':')[:11]
            dec = simbad_coord.dec.to_string(unit=units.deg, sep=':')[:11]
            sep = cand_coord.separation(simbad_coord).arcminute
            simbad_result_table.append({
                'name': result["MAIN_ID"],
                'search_term': search_term,
                'ra': ra,
                'dec': dec,
                'sep': sep,
            })

    # Perform atnf query
    atnf_query = psrqpy.QueryATNF(
        coord1=candidate.ra_hms,
        coord2=candidate.dec_dms,
        radius=float(arcmin)/60,
        params=["PSRJ", "NAME", "P0", "DM", "S400", "RAJ", "DECJ"],
    ).pandas
    atnf_result_table = []
    # Reformat the result into the format we want
    if atnf_query is not None:
        for index, pulsar in atnf_query.iterrows():
            # check for psrqpy missing data
            if "PSRJ" in pulsar.keys():
                name = pulsar["PSRJ"]
            elif "NAME" in pulsar.keys():
                name = pulsar["NAME"]
            else:
                name = None
            atnf_coord = SkyCoord(pulsar["RAJ"], pulsar["DECJ"], unit=(units.hour, units.deg), frame='icrs')
            sep = cand_coord.separation(atnf_coord).arcminute
            atnf_result_table.append({
                'name': name,
                'period': pulsar["P0"],
                'dm': pulsar["DM"],
                's400': pulsar["S400"],
                'sep': sep,
            })

    # Perform voevent database query https://voeventdbremote.readthedocs.io/en/latest/notebooks/00_quickstart.html
    # conesearch skycoord and angle error
    cand_err = Angle(arcmin,  unit=units.arcmin)
    # cand_err = Angle(5,  unit=units.deg)
    cone = (cand_coord, cand_err)

    my_filters = {
        FilterKeys.role: 'observation',
        FilterKeys.authored_since: time.tt.datetime - timedelta(hours=1),
        FilterKeys.authored_until: time.tt.datetime + timedelta(hours=1),
        # FilterKeys.authored_since: time.tt.datetime - timedelta(days=1),
        # FilterKeys.authored_until: time.tt.datetime + timedelta(days=1),
        FilterKeys.cone: cone,
        }
    voevent_list = apiv1.list_ivorn(
        filters=my_filters,
        order=OrderValues.author_datetime_desc,
    )
    voevents = []
    for ivorn in voevent_list:
        xml_packet = apiv1.packet_xml(ivorn)
        # Record xml ivorn into database
        xml_obj = models.xml_ivorns.objects.filter(ivorn=ivorn)
        if xml_obj.exists():
            xml_obj = xml_obj.first()
        else:
            xml_obj = models.xml_ivorns.objects.create(ivorn=ivorn)
        xml_id = xml_obj.id
        parsed_xml = parsed_VOEvent(None, packet=xml_packet.decode())
        # Check for ra and dec data
        if None in (parsed_xml.ra, parsed_xml.dec):
            ra = None
            dec = None
            sep = None
        else:
            voevent_coord = SkyCoord(parsed_xml.ra, parsed_xml.dec, unit=(units.deg, units.deg), frame='icrs')
            ra  = voevent_coord.ra.to_string(unit=units.hour, sep=':')[:11]
            dec = voevent_coord.dec.to_string(unit=units.deg, sep=':')[:11]
            sep = cand_coord.separation(voevent_coord).arcminute
        voevents.append({
            "telescope" : parsed_xml.telescope,
            "event_type" : parsed_xml.event_type,
            "ignored" : parsed_xml.ignore,
            "source_type" : parsed_xml.source_type,
            "trig_id" : parsed_xml.trig_id,
            'ra': ra,
            'dec': dec,
            'sep': sep,
            "xml" : xml_id,
        })

    context = {
        'candidate': candidate,
        'rating': rating,
        'time': time,
        'sep_arcmin': sep_arcmin,
        'simbad_result_table': simbad_result_table,
        'atnf_result_table': atnf_result_table,
        'arcmin_search': arcmin,
        'cand_type_choices': models.CAND_TYPE_CHOICES,
        'voevents' : voevents,
    }
    return render(request, 'candidate_app/candidate_rating_form.html', context)


def voevent_view(request, id):
    ivorn = models.xml_ivorns.objects.filter(id=id).first().ivorn
    xml_packet = apiv1.packet_xml(ivorn)
    v = voeventparse.loads(xml_packet)
    xml_pretty_str = voeventparse.prettystr(v)
    return HttpResponse(xml_pretty_str, content_type='text/xml')


@login_required
def token_manage(request):
    u = request.user
    token = Token.objects.filter(user=u).first()
    return render(request, 'candidate_app/token_manage.html', {"token":token})


@login_required
def token_create(request):
    u = request.user
    token = Token.objects.filter(user=u)
    if token.exists():
        token.delete()
    new_token = Token.objects.create(user=u)
    #return render(request, 'candidate_app/token_manage.html', {"token":new_token})
    return redirect(reverse('token_manage'))


@login_required
@api_view(['POST'])
@transaction.atomic
def candidate_update_rating(request, id):
    logger.debug(request.data)
    candidate = models.Candidate.objects.filter(id=id).first()
    if candidate is None:
        raise ValueError("Candidate not found")
    logger.debug('candidate obj %s', candidate)

    rating = models.Rating.objects.filter(candidate=candidate, user=request.user).first()
    if rating is None:
        # User hasn't made a rating of this cand so make one
        rating = models.Rating(
            candidate=candidate,
            user=request.user,
            rating=None,
        )
    logger.debug('rating obj %s', rating)

    # rfi = request.data.get('rfi', False)
    # if rating.rfi != rfi:
    #     logger.debug('setting rfi %s=>%s', rating.rfi, rfi)
    #     rating.rfi = rfi

    cand_type = request.data.get('cand_type', None)
    if cand_type:
        logger.debug('setting score %s=>%s', rating.cand_type, cand_type)
        rating.cand_type = cand_type

    score = request.data.get('rating', None)
    if score:
        logger.debug('setting score %s=>%s', rating.rating, score)
        rating.rating = score

    rating.save()

    # Update candidate notes
    notes = request.data.get('notes', '')
    if candidate.notes != notes:
        logger.debug('setting notes %s=>%s', candidate.notes, notes)
        candidate.notes = notes
    candidate.save()

    # Redirects to a random next candidate
    return redirect(reverse('candidate_random'))


@login_required
@api_view(['POST'])
@transaction.atomic
def candidate_update_catalogue_query(request, id):
    logger.debug(request.data)
    candidate = models.Candidate.objects.filter(id=id).first()
    if candidate is None:
        raise ValueError("Candidate not found")
    logger.debug('candidate obj %s', candidate)

    arcmin = request.data.get('arcmin', None)
    if arcmin:
        logger.debug(f'New query with {arcmin}')
        return candidate_rating(request, id, arcmin=arcmin)


@login_required
def candidate_random(request):
    user = request.user
    # Get unrated candidates
    unrated_cand = models.Candidate.objects.filter(rating__isnull=True)
    if not unrated_cand.exists():
        # No unrated candiate so see if user hasn't rated one
        unrated_cand = models.Candidate.objects.exclude(rating__user=user)
    if not unrated_cand.exists():
        # No candidates left so return to home screen
        return HttpResponse('<h3>No unrated canidate left</h3><h3><a href="/">Home Page</a></h3>')
    # Get random cand
    candidate = random.choice(list(unrated_cand))
    return redirect(reverse('candidate_rating', args=(candidate.id,)))


def candidate_table(request):
    # Get session data to keep filters when changing page
    candidate_table_session_data = request.session.get('current_filter_data', 0)
    print(candidate_table_session_data)

    # Check filter form
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = forms.CanidateFilterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            column_display = form.cleaned_data['column_display']
            observation_id_filter = form.cleaned_data['observation_id']
            rating_cutoff = form.cleaned_data['rating_cutoff']
            order_by = form.cleaned_data['order_by']
            asc_dec = form.cleaned_data['asc_dec']
            request.session['current_filter_data'] = {**form.cleaned_data}
    else:
        if candidate_table_session_data != 0:
            # Prefil form with previous session results
            form = forms.CanidateFilterForm(
                initial= candidate_table_session_data,
            )
            column_display = candidate_table_session_data['column_display']
            observation_id_filter = candidate_table_session_data['observation_id']
            rating_cutoff = candidate_table_session_data['rating_cutoff']
            order_by = candidate_table_session_data['order_by']
            asc_dec = candidate_table_session_data['asc_dec']
        else:
            form = forms.CanidateFilterForm()
            column_display = None
            observation_id_filter = None
            rating_cutoff = None
            order_by = 'avg_rating'
            asc_dec = '-'

    print(f"column_display: {column_display}")
    print(f"observation_id_filter: {observation_id_filter}")
    print(f"rating_cutoff: {rating_cutoff}")
    print(f"order_by: {order_by}")
    print(f"asc_dec: {asc_dec}")

    # Anontate with counts of different candidate type counts
    candidates = models.Candidate.objects.all().annotate(
        num_ratings=Count('rating'),
        avg_rating=Avg('rating__rating'),
        transient_count=Count('rating', filter=Q(rating__cand_type='T')),
        airplane_count=Count('rating', filter=Q(rating__cand_type='AP')),
        rfi_count=Count('rating', filter=Q(rating__cand_type='RFI')),
        sidelobe_count=Count('rating', filter=Q(rating__cand_type='SL')),
        alias_count=Count('rating', filter=Q(rating__cand_type='A')),
        chgcentre_count=Count('rating', filter=Q(rating__cand_type='CC')),
        scintillation_count=Count('rating', filter=Q(rating__cand_type='S')),
        pulsar_count=Count('rating', filter=Q(rating__cand_type='P')),
        other_count=Count('rating', filter=Q(rating__cand_type='O')),
    )

    # If user only wants to display a single column anotate it and return it's name
    if column_display is not None and column_display != "None":
        candidates = candidates.annotate(
            selected_count=Count('rating', filter=Q(rating__cand_type=column_display)),
        )
        # Filter count columns
        column_type_to_name = {
            "T": "N Tranisent",
            "AP": "N Airplane",
            "RFI": "N RFI",
            "SL": "N Sidelobe",
            "A": "N Alias",
            "CC": "N CHG Center",
            "S": "N Scintillation",
            "P": "N Pulsar",
            "O": "N Other",
        }
        selected_column = column_type_to_name[column_display]
    else:
        selected_column = None

    # Ratings filter
    if rating_cutoff is not None:
        candidates = candidates.filter(avg_rating__gte=rating_cutoff)

    # Obsid filter
    if observation_id_filter is not None:
        candidates = candidates.filter(obs_id__observation_id=observation_id_filter.observation_id)

    # Order by the column the user clicked or by avg_rating by default
    candidates = candidates.order_by(asc_dec + order_by, '-avg_rating')

    # Paginate
    paginator = Paginator(candidates, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'candidate_app/candidate_table.html', {'page_obj': page_obj, "form": form, "selected_column": selected_column})


@api_view(['POST'])
@transaction.atomic
def observation_create(request):
    obs = serializers.ObservationSerializer(data=request.data)
    if models.Observation.objects.filter(observation_id=request.data['observation_id']).exists():
        return Response("Observation already created so skipping", status=status.HTTP_201_CREATED)
    if obs.is_valid():
        obs.save()
        return Response(obs.data, status=status.HTTP_201_CREATED)
    logger.debug(request.data)
    return Response(obs.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
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
        #obs = models.Observation.objects.filter(observation_id=obsid).first()
        if png_file is None:
            return Response(
                "Missing png file", status=status.HTTP_400_BAD_REQUEST
            )
        if gif_file is None:
            return Response(
                "Missing gif file", status=status.HTTP_400_BAD_REQUEST
            )
        cand.save(png_path=png_file, gif_path=gif_file, filter=filter)
        return Response(cand.data, status=status.HTTP_201_CREATED)
    logger.debug(request.data)
    logger.error(cand.errors)
    return Response(cand.errors, status=status.HTTP_400_BAD_REQUEST)


def survey_status(request):
    # Order by the column the user clicked or by observation_id by default
    order_by = request.GET.get('order_by', 'observation_id')
    obs_list = models.Observation.objects.all().annotate(
        candidates=Count("candidate"),
        rated_candidates=Count(
            "candidate",
            filter=Q(candidate__rating__isnull=False)
        ),
    ).order_by(order_by)
    context = {'obs': obs_list}
    return render(request, 'candidate_app/survey_status.html', context)
