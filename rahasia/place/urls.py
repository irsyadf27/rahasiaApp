from django.conf.urls import url,include
from django.contrib import admin
from rest_framework import routers
from place.api import PlaceViewSet


router = routers.DefaultRouter()
router.register(r'place', PlaceViewSet)


urlpatterns = [
    url(r'^', include(router.urls))
]
