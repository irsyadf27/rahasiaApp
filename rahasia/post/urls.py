from django.conf.urls import url,include
from django.contrib import admin
from rest_framework import routers
from post.api import PostCreateAPIView, PostUpdateAPIView, \
	PostDeleteAPIView, PostListAPIView, \
	PostDetailAPIView, CommentCreateAPIView, \
	CommentDeleteAPIView


urlpatterns = [
    #url(r'^post/', PostViewSet),
    url(r'^$', PostListAPIView.as_view(), name='list'),
    url(r'^create/$', PostCreateAPIView.as_view(), name='create'),
    url(r'^(?P<pk>[0-9A-Fa-f-]+)/$', PostDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9A-Fa-f-]+)/edit/$', PostUpdateAPIView.as_view(), name='update'),
    url(r'^(?P<pk>[0-9A-Fa-f-]+)/delete/$', PostDeleteAPIView.as_view(), name='delete'),
    url(r'^(?P<pk>[0-9A-Fa-f-]+)/comment/$', CommentCreateAPIView.as_view(), name='create_comment'),
    url(r'^comment/(?P<pk>[0-9A-Fa-f-]+)/$', CommentDeleteAPIView.as_view(), name='delete_comment'),
]