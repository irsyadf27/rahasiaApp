from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import status, viewsets, permissions, serializers
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, ListCreateAPIView
from rest_framework.exceptions import NotFound

from message.permissions import ChatPermission, ThreadPermission
#from post.pagination import PostLimitOffsetPagination, PostPageNumberPagination
from message.models import MessageThread, MessageReply
from message.serializers import ChatListSerializer, ChatCreateSerializer, ReplyCreateSerializer
from message.pagination import ThreadPageNumberPagination

class ChatListAPIView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatListSerializer
    pagination_class = ThreadPageNumberPagination
    queryset = MessageThread.objects.all()

    def get_queryset(self):
        qs = MessageThread.objects.filter(Q(sender=self.request.user) | Q(recipient=self.request.user))
        return qs

class ChatCreateAPIView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatCreateSerializer
    queryset = MessageThread.objects.all()

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class ChatDeleteAPIView(DestroyAPIView):
    queryset = MessageThread.objects.all()
    serializer_class = ChatCreateSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAuthenticated, ThreadPermission]

class ChatReplyAPIView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, ChatPermission]
    serializer_class = ReplyCreateSerializer
    pagination_class = ThreadPageNumberPagination
    queryset = MessageReply.objects.all()
    #lookup_field = 'pk'

    def get_queryset(self):
        try:
            qs = MessageReply.objects.filter(thread=self.kwargs['pk'])
            unread_thread = MessageThread.objects.filter(pk=self.kwargs['pk'], unread_by__in=[self.request.user])
            if unread_thread.exists():
                unread_thread.first().unread_by.clear()
        except MessageReply.DoesNotExist:
            raise NotFound('Objects Not Found')
        return qs

    def perform_create(self, serializer):
        qs = MessageThread.objects.all()
        thread_obj = get_object_or_404(qs, pk=self.kwargs['pk'])
        thread_obj.unread_by.clear()
        if thread_obj.recipient == self.request.user:
            thread_obj.unread_by.add(thread_obj.sender)
        else:
            thread_obj.unread_by.add(thread_obj.recipient)
        serializer.save(thread=thread_obj, creator=self.request.user)