from django.shortcuts import render
from django.db import transaction

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from . import models, serializers

import logging
logger = logging.getLogger(__name__)

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