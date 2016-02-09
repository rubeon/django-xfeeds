from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.files import File
from django.contrib.contenttypes.fields import GenericRelation
from .tag import TaggedItem, SeenItem
from .media import CachedImage
# from ..parser import tasks

import os

from django.core.urlresolvers import reverse

import logging
logger = logging.getLogger(__name__)

class Feed(models.Model):
    """
    Model for feeds being tracked
    """
    # local metadata
    subscribers = models.ManyToManyField(User)
    feed_url = models.CharField(max_length=255)
    feed_title = models.CharField(max_length=255)
    
    date_added = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=False)

    # RSS metadata    
    language = models.CharField(blank=True, max_length=255)
    copyright = models.TextField(blank=True)
    
    author = models.CharField(blank=True, max_length=255)
    
    managingEditor = models.EmailField(blank=True)
    webMaster = models.EmailField(blank=True)

    pubDate = models.DateTimeField(auto_now=False)
    lastBuildDate = models.DateTimeField(auto_now=False)
    generator = models.CharField(blank=True, max_length=255)
    docs = models.URLField(blank=True)
    cloud = models.TextField(blank=True)
    ttl = models.IntegerField(default=3600)
    image = models.ForeignKey('CachedImage', null=True)
    icon = models.FileField(blank=True, upload_to="xfeeds/feed_icons/")
    rating = models.CharField(blank=True, max_length=255)
    textInput = models.CharField(blank=True, max_length=255)
    skipHours =  models.IntegerField(default=0)
    skipDays = models.IntegerField(default=0)
    
    link = models.URLField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    tags = GenericRelation(TaggedItem, related_query_name="feeds")
    
    def get_absolute_url(self):
        return reverse('feed-detail', kwargs={'pk':self.pk})
        
    def __unicode__(self):
        if len(self.feed_title) > 0:
            return self.feed_title
        else:
            return self.feed_url
    
class FeedCategory(models.Model):
    title = models.CharField(max_length=255)
    feeds = models.ManyToManyField('Feed')


class UnseenFeedItemsManager(models.Manager):
    def for_user(self, user):
        seen_by = self.model.seen.filter(user=user)
        if len(seen_by):
            return True
        else:
            return False
        # return super(UnseenFeedItemsManager, self).seen.get_queryset().filter(user=user)
        

class FeedItem(models.Model):
    """
    Keeps track of individual items in feeds
    """
    source = models.ForeignKey('Feed')
    guid = models.CharField(max_length=255)
    pubDate = models.DateTimeField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField()
    author = models.CharField(max_length=255)
    comments = models.URLField()
    
    tags = GenericRelation(TaggedItem, related_query_name="feeditems")
    seen = GenericRelation(SeenItem, related_query_name="feeditem_seen")
    
    # objects = models.Manager()
    # unread_items = UnseenFeedItemsManager()
    
    def seen_by(self, user):
        """
        returns True is this has been seen by user
        """
        if self.seen.filter(user=user):
            return True
        else:
            return False
    
    def __unicode__(self):
        if len(self.title) > 0:
            return self.title
        else:
            return self.link
    
class FeedItemCategory(models.Model):
    title = models.CharField(max_length=255)
    items = models.ManyToManyField('FeedItem')
    

# class CachedImage(models.Model):
#     url = models.URLField(max_length=255, unique=True)
#     image = models.ImageField(upload_to="cached_images", blank=True)
#     create_date = models.DateTimeField(auto_now_add=True)
#     update_date = models.DateTimeField(auto_now=True)
# 
#     TIMEOUT=3600 # in seconds ..?
#     
#     def cache(self):
#         """
#         Store image locally if we have a URL
#         """
# 
#         if self.url and not self.image:
#             ## not sure how this is going to fail on gigantic files, but guess
#             # we'll see (after we've DOS'd ourselves a few times)
#             res = urllib2.urlopen(self.url)
#             fd = tempfile.TemporaryFile()
#             fd.write(res.read())
#             fd.seek(0)
#             self.image.save(os.path.basename(self.url),File(fd))
#             self.save()
#     
#     @property
#     def stale(self):
#         return timezone.now() > self.TIMEOUT