from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.exceptions import NotFound, NotAcceptable
from message.models import MessageThread, MessageReply
from message.fake import commerce, name
import random

class ChatListSerializer(serializers.ModelSerializer):
    read = serializers.SerializerMethodField()

    class Meta:
        model = MessageThread
        fields = ('pk', 'title', 'content_type', 'object_pk', 'created_at', 'updated_at', 'read', )

    def get_read(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        return user not in obj.unread_by.all()

class ChatCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageThread
        fields = ('pk', 'title', 'content_type', 'object_pk', 'created_at', 'updated_at',)
        read_only_fields = ('title', 'created_at', 'updated_at',)

    def create(self, validated_data):
        n = name.Name()
        c = commerce.Commerce()
        list_title = [n.findName(), n.title(), c.productName(), c.productNameWithColor()]
        title = random.choice(list_title)
        validated_data['recipient'] = None

        try:
            ct = ContentType.model_class(validated_data.get('content_type', None))
            data = ct.objects.get(pk=validated_data.get('object_pk', None))
            validated_data['recipient'] = data.creator
        except ct.DoesNotExist:
            raise NotFound('Object Not Found')

        if not validated_data.get('recipient', None):
            raise NotFound('Recipient Not Found')

        if validated_data.get('sender', None) == validated_data.get('recipient', None):
            raise NotAcceptable('Cannot Chat With Your Self!!!!')

        obj = MessageThread.objects.filter(
            (
                (Q(sender=validated_data.get('sender', None)) | Q(sender=validated_data.get('recipient', None))) &
                (Q(recipient=validated_data.get('sender', None)) | Q(recipient=validated_data.get('recipient', None)))
            ),
            content_type=validated_data.get('content_type', None),
            object_pk=validated_data.get('object_pk', None),
            )
        if not obj.exists():
            validated_data['title'] = title
            obj = MessageThread.objects.create(**validated_data)
            obj.unread_by.add(validated_data.get('recipient', None))
            return obj
        return obj.first()

class ReplyCreateSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = MessageReply
        fields = ('pk', 'thread', 'sender', 'content', 'created_at', )
        read_only_fields = ('thread', 'created_at', )

    def get_sender(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            
        if obj.creator == user:
            return "Me"
        return "Other"