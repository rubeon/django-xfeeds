from django.db import models
from django.core.files import File

import urllib.request
import datetime
import time
import tempfile
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

TIMEOUT=3600 # check after 1 hour

class CachedImage(models.Model):
    url = models.URLField(max_length=255, unique=True)
    image = models.ImageField(upload_to="cached_images", blank=True)
    create_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    update_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    TIMEOUT=datetime.timedelta(seconds=TIMEOUT)
    
    def cache(self):
        """
        Store image locally if we have a URL
        """

        if self.url:
            ## not sure how this is going to fail on gigantic files, but guess
            # we'll see (after we've DOS'd ourselves a few times)
            res = urllib.request.urlopen(self.url)
            modified = time.strptime(res.headers['last-modified'], '%a, %d %b %Y %H:%M:%S %Z')
            print("=== ", modified)
            if modified > self.update_date.timetuple():
                # need to be re-cached
                logger.info("Upstream file %s has been updated, time to re-download" % self.url)
                fd = tempfile.TemporaryFile()
                fd.write(res.read())
                fd.seek(0)
                self.image.save(os.path.basename(self.url),File(fd))
            self.save()
    
    @property
    def stale(self):
        age = timezone.now() - self.update_date
        return age > self.TIMEOUT
