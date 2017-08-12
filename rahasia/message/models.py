from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from softdelete.models import SoftDeletionModel
import uuid

class MessageThread(SoftDeletionModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    users = models.ManyToManyField(
        User,
        related_name='conversations',
    )
    unread_by = models.ManyToManyField(
        User,
        related_name='unread_conversations',
        blank=True,
    )
    title = models.CharField(max_length=200, blank=True)

    content_type = models.ForeignKey(
        ContentType, related_name='content_type_set_for_%(class)s')

    #object_pk = models.PositiveIntegerField('object ID')
    object_pk = models.UUIDField()
    object_message = GenericForeignKey(ct_field='content_type', fk_field='object_pk')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __unicode__(self):
        return self.title

    def get_last_message(self):
        try:
            return self.messages.order_by('-created_at')[0]
        except IndexError:
            return None

class MessageReply(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(MessageThread, related_name='messages')
    creator = models.ForeignKey(User, related_name='messages')
    content = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']