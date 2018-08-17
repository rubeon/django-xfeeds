import logging
from django import template
from django.db.models import Count
from ..models.feed import Feed


register = template.Library()

LOGGER=logging.getLogger(__name__)

@register.simple_tag
def seen(user, item):
    """
    returns unread items for a user?
    """
    print("---", item.seen_by(user))
    return item.seen_by(user)

@register.simple_tag(takes_context=True)
def my_feeds(context):
    print(20*'-')
    if context['request'].user.is_authenticated:
        user = context['request'].user
        feed_list = Feed.objects.filter(subscribers=user).order_by('feed_title')
    else:
        # just grab a bunch of feeds
        feed_list = []
    print(feed_list)
    return feed_list

@register.simple_tag
def top_feeds():
    feed_list = Feed.objects.annotate(num_subs=Count('subscribers'))\
        .order_by('num_subs')
    return feed_list

@register.simple_tag    
def busy_feeds(limit=10):
    LOGGER.debug('busy_feeds entered')
    feed_list = Feed.objects.annotate(num_items=Count('feeditem')).order_by('-num_items')[:limit]
    return feed_list