from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.generics import DestroyAPIView, ListCreateAPIView

from message.permissions import ChatPermission, ThreadPermission
#from post.pagination import PostLimitOffsetPagination, PostPageNumberPagination
from message.models import MessageThread, MessageReply
from message.serializers import ChatCreateSerializer, ReplyCreateSerializer

class ChatCreateAPIView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatCreateSerializer
    queryset = MessageThread.objects.all()

    def get_queryset(self):
        qs = MessageThread.objects.filter(users__in=[self.request.user])
        return qs

    #def perform_create(self, serializer):
    #    serializer.save()

class ChatDeleteAPIView(DestroyAPIView):
    queryset = MessageThread.objects.all()
    serializer_class = ChatCreateSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAuthenticated, ThreadPermission]

class ChatReplyAPIView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, ChatPermission]
    serializer_class = ReplyCreateSerializer
    queryset = MessageReply.objects.all()
    #lookup_field = 'pk'

    def get_queryset(self):
        qs = MessageReply.objects.filter(thread=self.kwargs['pk'])
        return qs

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)