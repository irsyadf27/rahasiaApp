from django.shortcuts import get_object_or_404
from django.contrib.gis import geos
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from rest_framework import status, viewsets, permissions
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, DestroyAPIView, \
    ListAPIView, UpdateAPIView, \
    RetrieveAPIView, RetrieveUpdateAPIView, \
    ListCreateAPIView, RetrieveDestroyAPIView

from geopy.geocoders import Nominatim
from geopy.exc import GeopyError

from post.permissions import PostPermission
from post.pagination import PostLimitOffsetPagination, PostPageNumberPagination
from post.models import Post, Comment
from post.serializers import PostCreateSerializer, PostListSerializer, \
    PostUpdateSerializer, PostDetailSerializer, \
    CommentSerializer, CommentCreateSerializer

import json

class PostCreateAPIView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostCreateSerializer
    queryset = Post.objects.all()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

class PostUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, PostPermission]
    serializer_class = PostUpdateSerializer
    queryset = Post.objects.all()
    lookup_field = 'pk'

    def perform_update(self, serializer):
        serializer.save(creator=self.request.user)

class PostDeleteAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAuthenticated, PostPermission]

class PostListAPIView(ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PostPageNumberPagination

    def get_queryset(self):
        qs = Post.objects.all()
        radius = self.request.query_params.get('rad', 50)
        latitude = self.request.query_params.get('lat', None)
        longitude = self.request.query_params.get('lon', None)

        if latitude and longitude:
            pnt = geos.GEOSGeometry('POINT(' + str(longitude) + ' ' + str(latitude) + ')', srid=4326)
            qs = qs.filter(location__distance_lte=(pnt, D(km=radius)))
            qs = qs.annotate(distance=Distance('location', pnt))
        return qs

class PostDetailAPIView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAuthenticated, PostPermission]

class CommentCreateAPIView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentCreateSerializer
    queryset = Comment.objects.none()

    def perform_create(self, serializer):
        qs_p = Post.objects.all()
        post = get_object_or_404(qs_p, pk=self.kwargs['pk'])
        serializer.save(creator=self.request.user, post=post)

class CommentDeleteAPIView(RetrieveDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, PostPermission]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()