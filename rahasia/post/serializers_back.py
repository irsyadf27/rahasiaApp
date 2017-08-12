from post.models import Post
from rest_framework import serializers

from django.contrib.gis import geos
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import WKTReader

from django.core.exceptions import ObjectDoesNotExist

from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import json

from place.models import Place

class PostSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    num_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('pk', 'status', 'image', 'address', 'location', 'likes', 'dislikes', 'num_comments', 'created_at')
        read_only_fields = ('address', 'created_at', )

    def get_likes(self, obj):
        return obj.get_number_of_likes(obj).count()

    def get_dislikes(self, obj):
        return obj.get_number_of_dislikes(obj).count()

    def get_num_comments(self, obj):
        return obj.get_number_of_comments(obj).count()

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        if not validated_data['location']:
            try:
                lokasi = Place.objects.filter(active=True, creator=user).first()
                validated_data['address'] = lokasi.address
                validated_data['state'] = lokasi.state
                validated_data['country'] = lokasi.country
                validated_data['location'] = lokasi.location
            except ObjectDoesNotExist:
                raise serializers.ValidationError('Place not exists')
        else:
            try:
                addr = json.loads(str(validated_data['location']))
                getter = geocoder.reverse("%s, %s" % (addr['coordinates'][1], addr['coordinates'][0])).raw
                validated_data['address'] = getter['display_name']
                validated_data['state'] = getter['address']['state']
                validated_data['country'] = getter['address']['country_code']
                point = "POINT(%s %s)" % (getter['lon'], getter['lat'])
                validated_data['location'] = geos.fromstr(point)
            except (GeopyError, ValueError):
                raise serializers.ValidationError('Error')

        return Post.objects.create(**validated_data)

class PostDetailSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    num_comments = serializers.SerializerMethodField()
    comments = serializers.StringRelatedField(many=True)

    class Meta:
        model = Post
        fields = ('pk', 'status', 'image', 'address', 'location', 'likes', 'dislikes', 'num_comments', 'comments', 'created_at')
        read_only_fields = ('address', 'created_at', )

    def get_likes(self, obj):
        return obj.get_number_of_likes(obj).count()

    def get_dislikes(self, obj):
        return obj.get_number_of_dislikes(obj).count()

    def get_num_comments(self, obj):
        return obj.get_number_of_comments(obj).count()