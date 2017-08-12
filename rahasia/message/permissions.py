from rest_framework import permissions
from message.models import MessageThread, MessageReply

class ChatPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        chat = MessageThread.objects.get(pk=view.kwargs['pk'])
        return request.user in chat.users.all()

    def has_object_permission(self, request, view, obj):
        return request.user in obj.thread.users.all()

class ThreadPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.users.all()