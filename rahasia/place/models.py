from __future__ import unicode_literals


from django.contrib.auth.models import User

from django.contrib.gis import geos
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import WKTReader

from django.db import models
from rest_framework import serializers

from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import json

class Place(models.Model):
    creator = models.ForeignKey(User, related_name='places')

    name = models.CharField(max_length=200, blank=True)

    address = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    location = gis_models.PointField(u"longitude/latitude",
                                     geography=True, blank=True, null=True)

    gis = gis_models.GeoManager()
    objects = models.Manager()

    active = models.BooleanField(default=False)

    class Meta:
        unique_together = ('creator', 'location')

    def __unicode__(self):
        return self.name

    '''def save(self, **kwargs):
        geocoder = Nominatim()
        if not self.location:
            try:
                addr = self.name.encode('utf-8')
                getter = geocoder.geocode(addr, addressdetails=True).raw
            except (GeopyError, ValueError):
                raise serializers.ValidationError('Error')
        else:
            try:
                addr = geos.wkt_regex.match(str(self.location)).group(3)
                wkt_r = WKTReader()
                a = wkt_r.read(addr)

                getter = geocoder.reverse("%s, %s" % (a.y, a.x)).raw
            except (GeopyError, ValueError):
                raise serializers.ValidationError('Error')

        self.address = getter['display_name']
        self.state = getter['address']['state']
        self.country = getter['address']['country_code']
        point = "POINT(%s %s)" % (getter['lon'], getter['lat'])
        self.location = geos.fromstr(point)
        self.name = getter['display_name']
        self.active = True

        qs = type(self).objects.filter(active=True, creator=self.creator)
        qs.update(active=False)
                
        super(Place, self).save()'''