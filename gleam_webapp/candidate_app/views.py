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

import random
from astropy.time import Time

from . import models, serializers

import logging
logger = logging.getLogger(__name__)

def home_page(request):
    return render(request, 'candidate_app/home_page.html')


@login_required
def candidate_rating(request, id):
    candidate = get_object_or_404(models.Candidate, id=id)

    # Convert time to readable format
    time = Time(Time(candidate.obs_id.starttime, format='gps'), format='iso', scale='utc')

    # Grab any previous ratings
    u = request.user
    rating = models.Rating.objects.filter(candidate=candidate, user=u).first()

    # Convert seperation to arcminutes
    sep_arcmin = candidate.can_nks_sep_deg * 60

    context = {
        'candidate': candidate,
        'rating': rating,
        'time': time,
        'sep_arcmin': sep_arcmin,
    }
    return render(request, 'candidate_app/candidate_rating_form.html', context)


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
    # Order by the column the user clicked or by observation_id by default
    order_by = request.GET.get('order_by', '-avg_rating')
    candidates = models.Candidate.objects.annotate(
        num_ratings=Count('rating'),
        avg_rating=Avg('rating__rating'),
        transient_count=Count('rating', filter=Q(rating__cand_type='T')),
        rfi_count=Count('rating', filter=Q(rating__cand_type='RFI')),
        airplane_count=Count('rating', filter=Q(rating__cand_type='A')),
        sidelobe_count=Count('rating', filter=Q(rating__cand_type='SL')),
    ).order_by(order_by)

    # candidates = filter_claims(request, candidates)

    # rating_cutoff = get_rating_cutoff(request)
    # min_ratings = get_min_ratings(request)
    # sigma_cutoff = get_sigma_cutoff(request)

    # if rating_cutoff is not None:
    #     candidates = candidates.filter(avg_rating__gte=rating_cutoff)
    # if min_ratings is not None:
    #     candidates = candidates.filter(num_ratings__gte=min_ratings)
    # if sigma_cutoff is not None:
    #     candidates = candidates.filter(sigma__gte=sigma_cutoff)

    paginator = Paginator(candidates, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'candidate_app/candidate_table.html', {'page_obj': page_obj})


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
    cand = serializers.CandidateSerializer(data=request.data)
    png_file = request.data.get("png")
    if cand.is_valid():
        # Find obsid
        #obs = models.Observation.objects.filter(observation_id=obsid).first()
        if png_file is None:
            return Response(
                "Missing png file", status=status.HTTP_400_BAD_REQUEST
            )
        cand.save(png_path=png_file)
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