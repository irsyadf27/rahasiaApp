from rest_framework import permissions
from message.models import MessageThread, MessageReply
from rest_framework.exceptions import NotFound

class ChatPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            chat = MessageThread.objects.get(pk=view.kwargs['pk'])
        except MessageThread.DoesNotExist:
            raise NotFound("Object Not Found")
            
        return (chat.sender == request.user) or (chat.recipient == request.user)

    def has_object_permission(self, request, view, obj):
        return (obj.thread.sender == request.user) or (obj.thread.recipient == request.user)

class ThreadPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user in obj.users.all()