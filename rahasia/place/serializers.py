from rest_framework import serializers

from django.contrib.gis import geos
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import WKTReader

from geopy.geocoders import Nominatim
from geopy.exc import GeopyError, GeocoderTimedOut

from place.models import Place
import json

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ('pk', 'name', 'address', 'location', 'active', )
        read_only_fields = ('address', )
        
    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        geocoder = Nominatim()
        if not validated_data['location']:
            try:
                addr = validated_data['name'].encode('utf-8')
                getter = geocoder.geocode(addr, timeout=5, addressdetails=True).raw
            except (GeopyError, ValueError, AttributeError) as e:
                raise serializers.ValidationError(e)
        else:
            try:
                '''addr = geos.wkt_regex.match(str(self.location)).group(3)
                wkt_r = WKTReader()
                a = wkt_r.read(addr)'''
                addr = json.loads(str(validated_data['location']))
                getter = geocoder.reverse("%s, %s" % (addr['coordinates'][1], addr['coordinates'][0]), timeout=5).raw
            except (GeopyError, ValueError, AttributeError) as e:
                raise serializers.ValidationError(e)

        validated_data['address'] = getter['display_name']
        validated_data['state'] = getter['address']['state']
        validated_data['country'] = getter['address']['country_code']
        point = "POINT(%s %s)" % (getter['lon'], getter['lat'])
        validated_data['location'] = geos.fromstr(point)
        validated_data['name'] = getter['display_name']
        validated_data['active'] = True

        qs = Place.objects.filter(active=True, creator=user)
        qs.update(active=False)
                
        return Place.objects.create(**validated_data)

    def update(self, instance, validated_data):
        qs = Place.objects.filter(active=True, creator=instance.creator)
        if instance.pk:
            qs = qs.exclude(pk=instance.pk)
        qs.update(active=False)

        instance.active = True

        instance.save()
        return instance
