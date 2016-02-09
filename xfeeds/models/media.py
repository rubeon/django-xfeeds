from django.db import models
from django.core.files import File

import urllib2
import datetime
import tempfile
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

TIMEOUT=3600 # check after 1 hour

class CachedImage(models.Model):
    url = models.URLField(max_length=255, unique=True)
    image = models.ImageField(upload_to="cached_images", blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    TIMEOUT=datetime.timedelta(seconds=TIMEOUT)
    
    def cache(self):
        """
        Store image locally if we have a URL
        """

        if self.url:
            ## not sure how this is going to fail on gigantic files, but guess
            # we'll see (after we've DOS'd ourselves a few times)
            res = urllib2.urlopen(self.url)
            modified = res.info().getdate('last-modified')
            if modified > self.update_date:
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
