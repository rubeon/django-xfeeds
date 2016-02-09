import feedparser
import logging
import urllib2
import os
from datetime import datetime
from time import mktime
from pprint import pprint, pformat
from BeautifulSoup import BeautifulSoup as soup
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from ..models import Feed
from ..models import FeedItem
from ..models import TaggedItem
from ..models import CachedImage

logger = logging.getLogger(__name__)

def get_cached_image(url):
    """
    Utility to cache images
    """
    # first, see if the URL has already been cached
    try:
        cimage = CachedImage.objects.get(url=url)
    except CachedImage.DoesNotExist:
        cimage = CachedImage(url=url)
        cimage.save()
    cimage.cache()
    return cimage

def url_to_feed(url):
    """
    takes a URL, returns the feed object or None
    """
    logger.debug("%s.url_to_feed entered" % __name__)
    parsed_feed = parse_feed(url)['feed']
    # some minor validation...
    for required_key in ['title',]:
        if not parsed_feed.has_key(required_key):
            return None
    feed = add_feed(parsed_feed, url)
    # ok, now add the items

    return feed
    
def update_items(feed):
    """
    might be an instance method?
    """
    logger.debug("%s.update_items entered" % __name__)
    items = parse_feed(feed.feed_url)['items']
    res = add_items(feed, items)
    return res

def get_feed_image(parsed_feed):
    """
    Figures out how this precious little snowflake defines its image
    returns it as a django File object
    """
    image = None
    
    for key in ['image']:
        if hasattr(parsed_feed, key):
            image_struct = parsed_feed[key]
            logger.info("Found image key %s: %s" % (key, image_struct))
            image = get_cached_image(image_struct.url)
            
            if image:
                continue
    return image

def get_feed_icon(parsed_feed):
    if hasattr(parsed_feed, 'icon'):
        image_url = parsed_feed['icon']
        logger.info("Found icon: %s"  % icon_url)
    
def add_feed(parsed_feed, feed_url):
    """
    Takes a feed dictionary, and adds it to the database
    if exists, returns the original
    """
    logger.debug("%s.add_feed entered" % __name__)
    logger.debug("feed_url: %s" % feed_url)
    logger.debug("feed: \n%s" % pformat(parsed_feed))

    if parsed_feed.has_key('links'):
        for link in parsed_feed['links']:
          if 'self' in link.values():
              # self-declared feed_url takes precendence
              # FIXME: let's see how that works out in practice...
              feed_url = link['href']
    # else:
    #     pprint(parsed_feed)
    #     raise ValidationError
    # check if this is a known feed
    if not parsed_feed.has_key('title'):
        pprint(parsed_feed)
    
    try:
        f = Feed.objects.get(feed_url=feed_url)
    except Feed.DoesNotExist:
        # needs to be added
        if parsed_feed.get('updated', None):
            updated = datetime.fromtimestamp(mktime(parsed_feed['updated_parsed']))
        else:
            updated = datetime.now()
        struct = {
            'feed_title': parsed_feed['title'],
            'language': parsed_feed.get('language', 'en'),
            'copyright': parsed_feed.get('copyright',''),
            'generator': parsed_feed.get('generator', ''),
            'link': parsed_feed['link'],
            'last_update': datetime.now(),
            'pubDate': updated,
            'lastBuildDate': updated,
            'skipHours': parsed_feed.get('skipHours', 1),
            'feed_url' : feed_url
        }
        struct['image'] = get_feed_image(parsed_feed)
        logger.debug(struct)
        f = Feed(**struct)
        f.save()
    return f
    
def add_items(feed, parsed_items):
    # feed: Feed object
    # parsed_items: list of items from the feedparser
    count = 0
    for item in parsed_items:
        # check of this has already been indexed
        print item['id']
        
        try:
            FeedItem.objects.get(guid=item['id'])
            continue
        except FeedItem.DoesNotExist:
            # figure out the pub_date
            if item.has_key('published_parsed'):
                pubDate = item['published_parsed']
            elif item.has_key('updated_parsed'):
                pubDate = item['updated_parsed']
                
            pubDate = datetime.fromtimestamp(mktime(pubDate))

            # ok, it's new
            # need to figure out content
            pprint(item)
            
            # if not item.has_key('description'):
            #     print "DOH!"
            #     logger.debug('description empty, look for content')
            #     description = item['content'][0]['value'] # wordpress weirdness
            # else:
            #     description = item['description']
            description = item['description']
            struct = {
                'source': feed,
                'guid': item['id'],
                'pubDate':  pubDate,
                'title': item.get('title', 'Untitled'),
                'description': description,
                'link': item['link'],
                'author': item.get('author', feed.author),
                'comments': item.get('comments',''),
                
            }
            pprint(struct)
            i = FeedItem(**struct)
            i.save()
            count = count + 1
    return count

def parse_feed(url):
    d = feedparser.parse(url)
    return d

    