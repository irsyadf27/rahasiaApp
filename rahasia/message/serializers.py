from rest_framework import serializers
from message.models import MessageThread, MessageReply
from message.fake import commerce, name
import random

class ChatCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageThread
        fields = ('pk', 'users', 'title', 'content_type', 'object_pk', 'created_at', 'updated_at',)
        read_only_fields = ('title', 'created_at', 'updated_at',)

    def create(self, validated_data):
        n = name.Name()
        c = commerce.Commerce()
        list_title = [n.findName(), n.title(), c.productName(), c.productNameWithColor()]
        title = random.choice(list_title)

        obj = MessageThread.objects.filter(
            users__in=validated_data.get('users', None),
            content_type=validated_data.get('content_type', None),
            object_pk=validated_data.get('object_pk', None),
            ).distinct()

        return obj
        '''obj, created = MessageThread.objects.get_or_create(
            users__in=validated_data.get('users', None),
            content_type=validated_data.get('content_type', None),
            object_pk=validated_data.get('object_pk', None),
            )
        print obj
        print created
        obj = MessageThread.objects.filter(
            users=validated_data.get('users', None),
            content_type=validated_data.get('content_type', None),
            object_pk=validated_data.get('object_pk', None),
            )
        print obj.query'''

class ReplyCreateSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    class Meta:
        model = MessageReply
        fields = ('pk', 'thread', 'sender', 'content', 'created_at', )
        read_only_fields = ('created_at', )

    def get_sender(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            
        if obj.creator == user:
            return "Me"
        return "Other"