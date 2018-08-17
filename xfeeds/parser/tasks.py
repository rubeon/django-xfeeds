import logging
import os
import ssl
import urllib.request
import feedparser

from datetime import datetime
from time import mktime, localtime
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
    res = parse_feed(url)

    # minor kluge here
    parsed_feed = res['feed']
    parsed_feed['etag'] = getattr(res, 'etag', None)
    parsed_feed['last_modified'] = getattr(res, 'last_modified', None)

    # pprintparsed_feed)
    # some minor validation...
    for required_key in ['title',]:
        if required_key not in parsed_feed:
            return None
    feed = add_feed(parsed_feed, url)
    # ok, now add the items
    feed_items = update_items(feed)
    return feed
    
def update_items(feed, force=False):
    """
    might be an instance method?
    """
    if feed.needs_update or force:
        LOGGER.debug("%s.update_items entered" % __name__)
        items = parse_feed(feed.feed_url, etag=feed.etag, modified=feed.last_update)['items']
        res = add_items(feed, items)
    else:
        print("Skipping (update not needed)")
        res = 0
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
        f.etag = parsed_feed['etag']
        f.last_modified = parsed_feed['last_modified']
        f.save()
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
            'feed_url' : feed_url,
            'etag' : parsed_feed['etag'],
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
        # pprint(item)
        if not id in item:
            item['id'] = item['link']
        pubDate = localtime()
        try:
            FeedItem.objects.get(guid=item['id'])
            continue
        # except KeyError as e:
        #     # item doesn't have a guid, for shame!
        #     item['id'] = item['link']
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

def find_feed(site):
    """
    Parses a page, and returns a list of 
    atom / RSS feeds
    """
    parsed_url = urllib.parse.urlparse(site)
    if not parsed_url.scheme:
        site = 'http://' + site 
        parsed_url = urllib.parse.urlparse(site)
        
    req = urllib.request.Request(
        site, 
        data=None, 
        headers={
            'User-Agent': FAKE_AGENT
        }
    )

    
    raw = urllib.request.urlopen(req).read()
    result = []
    possible_feeds = []
    html = soup(raw, features='html.parser')
    feed_urls = html.findAll("link", rel="alternate")
    for f in feed_urls:
        t = f.get("type",None)
        if t:
            if "rss" in t or "xml" in t:
                href = f.get("href",None)
                if href:
                    possible_feeds.append(href)
    parsed_url = urllib.parse.urlparse(site)
    if not parsed_url.scheme:
        parsed_url = urllib.parse.urlparse('http://' + site)
    base = parsed_url.scheme+"://"+parsed_url.hostname
    atags = html.findAll("a")
    for a in atags:
        href = a.get("href",None)
        if href:
            if "xml" in href or "rss" in href or "feed" in href:
                possible_feeds.append(base+href)
    for url in list(set(possible_feeds)):
        f = feedparser.parse(url)
        if len(f.entries) > 0:
            if url not in result:
                result.append(url)
    return(result)

def parse_feed(url, etag=None, modified=None):
    # use urllib to get the text
    d = feedparser.parse(url, etag=etag, modified=modified)
    # pprintd)
    return d