from rest_framework import viewsets, permissions
from rest_framework.decorators import list_route
from rest_framework.response import Response

from place.models import Place
from place.serializers import PlaceSerializer
from place.permissions import PlacePermission

from django.contrib.gis import geos
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import json

class PlaceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, PlacePermission]
    serializer_class = PlaceSerializer
    queryset = Place.objects.none()

    def get_queryset(self):
        return Place.objects.filter(creator=self.request.user)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)