# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from post.models import Comment, Post
import uuid

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    recipient = models.ManyToManyField(
        User,
        related_name='notifications',
    )

    unread_by = models.ManyToManyField(
        User,
        related_name='notification_unread',
        blank=True,
    )

    verb = models.CharField(max_length=200)

    content_type = models.ForeignKey(
        ContentType, related_name='content_type_set_for_%(class)s')

    object_pk = models.UUIDField()
    object_notification = GenericForeignKey(ct_field='content_type', fk_field='object_pk')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __unicode__(self):
        return "{} {}".format(self.verb, self.object_notification)

@receiver(post_save, sender=Comment)
def update_notification(sender, instance, created, **kwargs):
    if created:
        
        list_commented_users = Comment.objects.values_list('creator', flat=True).filter(post=instance.post).exclude(creator=instance.creator).distinct()
        if list_commented_users.exists():
            list_commented_users = list(list_commented_users)
            list_commented_users.append(instance.post.creator.pk)
        else:
            list_commented_users = [instance.post.creator.pk]

        list_users = User.objects.filter(pk__in=list_commented_users).exclude(pk=instance.creator.pk).distinct()

        ct = ContentType.objects.get_for_model(Post)
        obj, created_notif = Notification.objects.get_or_create(object_pk=instance.post.pk, content_type=ct, defaults={'verb': "New Comments on"})
        obj.recipient.add(*list_users)
        obj.unread_by.add(*list_commented_users)