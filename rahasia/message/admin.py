from django.contrib import admin

from message.models import MessageThread, MessageReply

admin.site.register(MessageThread)
admin.site.register(MessageReply)