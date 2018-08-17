import time

from django.core.management.base import BaseCommand, CommandError
from xfeeds.models import Feed
from xfeeds.parser import tasks

class Command(BaseCommand):
    """
    Update feeds that be needin' it
    """
    def add_arguments(self, parser):
        """
        Build argument parser
        """
        parser.add_argument('--force', dest='force', 
                                       type=str, 
                                       default='n')

        parser.add_argument('--id', '-i',  dest='id', 
                                           type=str, 
                                           default='', 
                                           help='Specify feed ID'
                            )
        parser.add_argument('--list', '-l',  dest='list', 
                                           type=str, 
                                           default='n', 
                                           help='Show more information'
                            )
    
    def handle(self, *args, **options):
        start = time.time()
        verbose = options['list'].lower() in ['y', 'yes']
        feed_list = Feed.objects.all()
        updated_feeds = 0
        updated_items = 0
        if options['force'].lower() in ['y', 'yes' ]:
            verbose and print("Using force")
            force = True
        else:
            force = False
        
        for feed in feed_list:
            verbose and print(feed.feed_title)
            # res = tasks.update_items(feed, force=force)
            res = tasks.url_to_feed(feed.feed_url)
            # if res > 0:
            #     updated_feeds += 1
            #     updated_items += res
        
        finish = time.time()
        
        print("Updated {} items / {} feeds in {} seconds".format(updated_items, updated_feeds, finish - start))
        
        
            