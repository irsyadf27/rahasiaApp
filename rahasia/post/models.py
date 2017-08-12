from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from django.contrib.gis import geos
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import WKTReader

from notifications.signals import notify
from post.utils import image_upload_handler

from softdelete.models import SoftDeletionModel
import uuid

class Post(SoftDeletionModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(User, related_name='posts')
    status = models.CharField(max_length=150)
    image = models.ImageField(upload_to=image_upload_handler, blank=True, null=True)

    address = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    location = gis_models.PointField(u"longitude/latitude",
                                     geography=True, blank=True, null=True)

    gis = gis_models.GeoManager()
    #objects = models.Manager()

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __unicode__(self):
        return self.status

    @staticmethod
    def get_number_of_likes(self):
        return self.reaction.filter(type=PostReaction.LIKE)

    @staticmethod
    def get_number_of_dislikes(self):
        return self.reaction.filter(type=PostReaction.DISLIKE)

    @staticmethod
    def get_number_of_comments(self):
        return self.comments

class Comment(SoftDeletionModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, related_name='comments')
    creator = models.ForeignKey(User)
    avatar = models.CharField(max_length=20)
    comment = models.CharField(max_length=200)

    address = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    location = gis_models.PointField(u"longitude/latitude",
                                     geography=True, blank=True, null=True)

    gis = gis_models.GeoManager()
    #objects = models.Manager()

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __unicode__(self):
        return self.comment

    def save(self, *args, **kwargs):
        notify.send(self.creator, recipient=self.content_object.author, action_object=self.content_object, target=self, verb="commented on")

class PostReaction(models.Model):
    LIKE = 'Like'
    DISLIKE = 'Dislike'

    REACTION_TYPES = [LIKE, DISLIKE]

    post = models.ForeignKey(Post, related_name='reaction')
    user = models.ForeignKey(User)

    type = models.CharField(max_length=10, choices=zip(
        REACTION_TYPES, REACTION_TYPES))

    def __unicode__(self):
        return "{}: {} {}".format(self.type, self.user.username, self.post.status)