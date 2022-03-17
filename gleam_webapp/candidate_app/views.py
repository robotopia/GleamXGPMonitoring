from django.shortcuts import render
from django.db import transaction

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from . import models, serializers

import logging
logger = logging.getLogger(__name__)

def home_page(request):
    return render(request, 'candidate_app/home_page.html')

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