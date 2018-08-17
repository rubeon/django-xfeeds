import time
import urllib.parse
import feedparser

from django.core.management.base import BaseCommand, CommandError
from xfeeds.models import Feed
from xfeeds.parser import tasks
from bs4 import BeautifulSoup as soup
from pprint import pprint
# Command to feed a bunch of content into the site
# This will go to a seeder page, and spider the first
# 100 feeds it can find

class Command(BaseCommand):
    """
    Spider a bunch o' goddam feeds
    """
    
    all_links = []
    rss_links = []
    spidered = []
    max_links = 500
    max_feeds = 500
    
    help = 'Add feeds starting with a seeder site'
    def add_arguments(self, parser):
        """
        Build argument parser
        """
        parser.add_argument('url', type=str)
        parser.add_argument('--max-links', '-l', dest='max_links', 
                                                 type=int, 
                                                 default=500, 
                                                 help="Maximum number of links "
                                                      "to spider (approx.)"
                            )
        parser.add_argument('--max-feeds', '-f', dest='max_feeds',
                                                 type=int, 
                                                 default=500, 
                                                 help="Maximum number of RSS"
                                                      "feeds to process "
                                                      "(approx.)"
                            )
    
    def spider(self, site):
        """
        grabs all the outgoing links from a site
        """
        # print("Spidering", site)
        if len(self.all_links) > self.max_links:
            print("Skipping (max_links)")
            return 
        try:
            rurl = urllib.parse.urlparse(site)
        except:
            print("Couldn't parse", site)
            return 
        self.spidered.append(site)
        pprint(self.spidered)
        try:
            html = soup(urllib.request.urlopen(site, timeout=1).read(), 'html.parser')
        except:
            return
        alist = html.find_all('a')
        links = [link.get('href') for link in alist]
        for link in links:
            # print(link)
            try:
                purl = urllib.parse.urlparse(link)
                if purl.netloc != rurl.netloc and \
                purl.scheme in ['http', 'https']:
                    self.all_links.append(link) and print("added", link)
                else:
                    continue
            except:
                continue
            finally:
                print("{} Processed {}".format(len(self.all_links), purl.netloc))
        # pprint(all_links)
        # return all_links
        for link in self.all_links:
            if link not in self.spidered:
                self.spider(link)
    
    
    def handle(self, *args, **options):
        start = time.time()
        print(options)
        self.max_links = options.get('max_links')
        self.max_feeds = options.get('max_feeds')
        url = options.get('url')
        print("Starting with", url)
        self.spider(url)
        
        print("Spidered {} sites".format(len(self.all_links)))
        for site in self.all_links:
            try:
                self.rss_links.extend(tasks.find_feed(site))
            except Exception as e:
                print("Skipping", site)
                print(str(e))
            finally:
                print("#", len(self.rss_links))
        pprint(self.rss_links)
        finish = time.time()
        print("Found {} RSS feeds in {} seconds"
            .format(len(self.rss_links), finish - start))
        for feed in self.rss_links:
            tasks.url_to_feed(feed)