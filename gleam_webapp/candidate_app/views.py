from django.shortcuts import render
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

import random

from . import models, serializers

import logging
logger = logging.getLogger(__name__)

def home_page(request):
    return render(request, 'candidate_app/home_page.html')


def candidate_rating(request, id):
    candidate = get_object_or_404(models.Candidate, id=id)

    u = request.user
    rating = models.Rating.objects.filter(candidate=candidate, user=u).first()

    context = {
        'candidate': candidate,
        #'rating': rating,
    }
    return render(request, 'candidate_app/candidate_rating_form.html', context)


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
            rfi=None,
            rating=None,
        )
    logger.debug('rating obj %s', rating)

    rfi = request.data.get('rfi', False)
    score = request.data.get('rating', None)

    if rating.rfi != rfi:
        logger.debug('setting rfi %s=>%s', rating.rfi, rfi)
        rating.rfi = rfi
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


def candidate_random(request):
    user = request.user
    # Get unrated candidates
    unrated_cand = models.Candidate.objects.filter(rating__isnull=True)
    if not unrated_cand.exists():
        # No unrated candiate so see if user hasn't rated one
        unrated_cand = models.Candidate.objects.exclude(rating__user=user)
    if not unrated_cand.exists():
        # No candidates left so return to home screen
        return redirect(reverse('home_page'))
    # Get random cand
    candidate = random.choice(list(unrated_cand))
    return redirect(reverse('candidate_rating', args=(candidate.id,)))


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
    return Response(cand.errors, status=status.HTTP_400_BAD_REQUEST)