from django.test import TestCase
from xfeeds.models import Feed
from xfeeds.models import FeedCategory
from xfeeds.models import FeedItem
from xfeeds.models import FeedItemCategory
from xfeeds.models import CachedImage
from xfeeds.parser import tasks
import os
from glob import glob
# Create your tests here.
class TestFeeds(TestCase):
    test_feeds = glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/test_feeds/*"))
    
    def setUp(self):
        self.feed_url_yb = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/test_feeds/youbitch.org.rss")
        self.feed_url_wp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/test_feeds/sistaweb.de.rss")
        self.feed_url_wp_new = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_test_feeds/jwz.org.rss")
        self.feed_url_invalid = "http://example.com/"
        
    def test_fetch_feed_yb(self):
        res = tasks.parse_feed(self.feed_url_yb)
        self.assertTrue(res.has_key('feed'))
        self.assertTrue(res.has_key('items'))
    
    def test_fetch_feed_wp(self):
        res=tasks.parse_feed(self.feed_url_wp)
        self.assertTrue(res.has_key('feed'))
        self.assertTrue(res.has_key('items'))
        
    def test_fetch_feed_invalid(self):
        res = tasks.url_to_feed(self.feed_url_invalid)
        self.assertFalse(isinstance(res, Feed))
    
    def test_add_new_feed_yb(self):
        res = tasks.url_to_feed(self.feed_url_yb)
        self.assertTrue(isinstance(res, Feed))

    def test_add_new_feed_wp(self):
        res = tasks.url_to_feed(self.feed_url_wp)
        self.assertTrue(isinstance(res, Feed))

    
    def test_add_new_items_yb(self):
        feed = tasks.url_to_feed(self.feed_url_yb)
        tasks.update_items(feed)
    
    def test_unreliable_feeds(self):
        for url in self.test_feeds:
            print url
            feed = tasks.url_to_feed(url)
            if feed:
                tasks.update_items(feed)
            
    def test_feed_with_site_image(self):
        """
        this should figure out the best site image
        and import it to the feed's `image` attribute
        """
        # known good feed
        url = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/test_feeds/feed_with_image_wp.rss")
        feed = tasks.url_to_feed(url)
        self.assertTrue(isinstance(feed.image, CachedImage))
        