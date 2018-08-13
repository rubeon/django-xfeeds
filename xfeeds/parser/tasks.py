import logging
import os
import ssl
import urllib.request
import feedparser

from datetime import datetime
from time import mktime
from pprint import pprint, pformat
from bs4 import BeautifulSoup as soup
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from ..models import Feed
from ..models import FeedItem
from ..models import TaggedItem
from ..models import CachedImage

LOGGER = logging.getLogger(__name__)
FAKE_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

feedparser.USER_AGENT = FAKE_AGENT

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
    # pprint"Url to feed entered")
    LOGGER.debug("%s.url_to_feed entered" % __name__)
    parsed_feed = parse_feed(url)['feed']
    # pprintparsed_feed)
    # some minor validation...
    for required_key in ['title',]:
        if required_key not in parsed_feed:
            return None
    feed = add_feed(parsed_feed, url)
    # ok, now add the items
    feed_items = update_items(feed)
    return feed
    
def update_items(feed):
    """
    might be an instance method?
    """
    LOGGER.debug("%s.update_items entered" % __name__)
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
            LOGGER.info("Found image key %s: %s" % (key, image_struct))
            image = get_cached_image(image_struct.url)
            
            if image:
                continue
    return image

def get_feed_icon(parsed_feed):
    if hasattr(parsed_feed, 'icon'):
        image_url = parsed_feed['icon']
        LOGGER.info("Found icon: %s"  % icon_url)
    
def add_feed(parsed_feed, feed_url):
    """
    Takes a feed dictionary, and adds it to the database
    if exists, returns the original
    """
    LOGGER.debug("%s.add_feed entered" % __name__)
    LOGGER.debug("feed_url: %s" % feed_url)
    LOGGER.debug("feed: \n%s" % pformat(parsed_feed))

    if 'links' in parsed_feed:
        for link in parsed_feed['links']:
          if 'self' in list(link.values()):
              # self-declared feed_url takes precendence
              # FIXME: let's see how that works out in practice...
              feed_url = link['href']
    # else:
    #     # pprintparsed_feed)
    #     raise ValidationError
    # check if this is a known feed
    # if 'title' not in parsed_feed:
    #     # pprintparsed_feed)
    #
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
        LOGGER.debug(struct)
        f = Feed(**struct)
        f.save()
    return f
    
def add_items(feed, parsed_items):
    # feed: Feed object
    # parsed_items: list of items from the feedparser
    count = 0
    for item in parsed_items:
        # check of this has already been indexed
        # pprintitem['id'])
        
        try:
            FeedItem.objects.get(guid=item['id'])
            continue
        except FeedItem.DoesNotExist:
            # figure out the pub_date
            if 'published_parsed' in item:
                pubDate = item['published_parsed']
            elif item.has_key('updated_parsed'):
                pubDate = item['updated_parsed']
                
            pubDate = datetime.fromtimestamp(mktime(pubDate))

            # ok, it's new
            # need to figure out content
            # pprintitem)
            
            # if not item.has_key('description'):
            #     print "DOH!"
            #     LOGGER.debug('description empty, look for content')
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
            # pprintstruct)
            i = FeedItem(**struct)
            i.save()
            count = count + 1
    return count

def get_feed(url):
    """
    Parses the page, and sees if it's an RSS page
    If not, grabs the first link it can find.
    """

def parse_feed(url):
    # use urllib to get the text
    # First, create a fake user agent. Some sites block bots. (boo)
    d = feedparser.parse(url)
    # pprintd)
    return d