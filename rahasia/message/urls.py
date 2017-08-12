from django.conf.urls import url,include
from django.contrib import admin
from rest_framework import routers
from message.api import ChatListAPIView, ChatCreateAPIView, ChatReplyAPIView, ChatDeleteAPIView

urlpatterns = [
    #url(r'^post/', PostViewSet),
    #url(r'^$', PostListAPIView.as_view(), name='list'),
    url(r'^$', ChatListAPIView.as_view(), name='list'),
    url(r'^create/$', ChatCreateAPIView.as_view(), name='create'),
    url(r'^(?P<pk>[0-9A-Fa-f-]+)/$', ChatReplyAPIView.as_view(), name='reply'),
    url(r'^(?P<pk>[0-9A-Fa-f-]+)/delete/$', ChatDeleteAPIView.as_view(), name='delete'),
]