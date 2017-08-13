from django.contrib.gis import geos
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import WKTReader
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from rest_framework import serializers, pagination
from rest_framework.exceptions import NotFound, NotAcceptable
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
from place.models import Place
from post.models import Post, Comment, PostReaction
#from post.pagination import PaginatedCommentSerializer
import json
import random

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('pk', 'avatar', 'comment', 'address', 'created_at', )

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('avatar', 'comment', 'location', )
        read_only_fields = ('avatar', )

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        avatar = Comment.objects.filter(post=validated_data['post'], creator=user).first()
        if avatar:
            validated_data['avatar'] = avatar.avatar
        else:
            get_author = Post.objects.filter(pk=validated_data['post'].pk).get().creator
            if get_author == user:
                validated_data['avatar'] = 'author'
            else:
                list_avatars = settings.LIST_AVATAR

                used_avatars = Comment.objects.values_list('avatar', flat=True).filter(post=validated_data['post']).distinct().order_by()
                
                available_avatar = list(set(list_avatars) - set(used_avatars))

                if len(available_avatar) > 0:
                    validated_data['avatar'] = random.choice(available_avatar)
                else:
                    validated_data['avatar'] = random.choice(list_avatars)

        if not validated_data['location']:
            try:
                lokasi = Place.objects.filter(active=True, creator=user).first()
                if not lokasi:
                    raise NotFound('Place not exists')

                validated_data['address'] = lokasi.address
                validated_data['state'] = lokasi.state
                validated_data['country'] = lokasi.country
                validated_data['location'] = lokasi.location
            except ObjectDoesNotExist:
                raise NotFound('Place not exists')

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
                raise NotFound('Error')

        return Comment.objects.create(**validated_data)
        
class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('status', 'image', 'location', )

    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        if not validated_data['location']:
            try:
                lokasi = Place.objects.filter(active=True, creator=user).first()
                if not lokasi:
                    raise NotFound('Place not exists')
                    
                validated_data['address'] = lokasi.address
                validated_data['state'] = lokasi.state
                validated_data['country'] = lokasi.country
                validated_data['location'] = lokasi.location
            except ObjectDoesNotExist:
                raise NotFound('Place not exists')
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
                raise NotFound('Error')

        return Post.objects.create(**validated_data)

class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('status', 'image', )

class PostListSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    num_comments = serializers.SerializerMethodField()
    distance = serializers.DecimalField(source='distance.km', max_digits=10, decimal_places=2, required=False, read_only=True)

    class Meta:
        model = Post
        fields = ('pk', 'status', 'image', 'address', 'likes', 'dislikes', 'num_comments', 'distance', 'created_at', )
        read_only_fields = ('distance', )
        
    def get_likes(self, obj):
        return obj.get_number_of_likes(obj).count()

    def get_dislikes(self, obj):
        return obj.get_number_of_dislikes(obj).count()

    def get_num_comments(self, obj):
        return obj.get_number_of_comments(obj).count()

class PostDetailSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    num_comments = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('pk', 'status', 'image', 'address', 'likes', 'dislikes', 'num_comments', 'comments', 'created_at', )

    def get_likes(self, obj):
        return obj.get_number_of_likes(obj).count()

    def get_dislikes(self, obj):
        return obj.get_number_of_dislikes(obj).count()

    def get_num_comments(self, obj):
        return obj.get_number_of_comments(obj).count()

    def get_comments(self, obj):
        #c_qs = Comment.objects.filter(post=obj.pk)
        #comments = CommentSerializer(c_qs, many=True).data
        #return comments
        c_qs = Comment.objects.filter(post=obj)
        paginator = pagination.PageNumberPagination()
        page = paginator.paginate_queryset(c_qs, self.context['request'])
        serializer = CommentSerializer(page, many=True, context={'request': self.context['request']})
        return serializer.data

class PostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = ('post', 'type', )

    def create(self, validated_data):
        obj, created = PostReaction.objects.get_or_create(post=validated_data.get('post', None), user=validated_data.get('user', None), defaults={"type": validated_data.get('type', None)})
        if not created:
            obj.type = validated_data.get('type', None)
            obj.save()
        return obj