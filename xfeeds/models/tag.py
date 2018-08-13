from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
import datetime

class TaggedItem(models.Model):
    """
    tag <-> object relatiion manager
    """
    tag = models.SlugField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    def __unicode__(self):
        return self.tag
        
class SeenItem(models.Model):
    """
    user <-> seen relation manager
    
    can be used to show whether a user has
    seen an object or not.
    Not sure how well this is going to handle large amounts of
    articles, but hey, we'll see.
    
    Usage: 
    * tag as seen
    >>> u = User.objects.get(username="admin")
    >>> fi = FeedItem.get(id=1)
    >>> s = SeenItem()
    >>> s.save()
    """
    seen = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return self.seen
        
    # def save(self, *args, **kwargs):
    #         
    #     super(SeenItem, self).save(*args, **kwargs)
    
    @property
    def last_seen(self):
        return self.last_modified
    
    @property
    def first_seen(self):
        return self.create_date
        
    def __unicode__(self):
        return "%s:%s" % (self.first_seen, self.last_modified)