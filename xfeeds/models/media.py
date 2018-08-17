from django.db import models
from django.core.files import File
from PIL import Image

import os
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
    
    def cache_image_directory_path(self, instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return 'cached_image_{0}/{1}.{2}'.format(instance.id, filename, 'jpeg')
    
    def cache(self, force=False):
        """
        Store image locally if we have a URL
        """

        if self.url:
            ## not sure how this is going to fail on gigantic files, but guess
            # we'll see (after we've DOS'd ourselves a few times)
            print("URL:", self.url)
            try:
                filename = os.path.split(self.url)[-1]
                res = urllib.request.urlopen(self.url)
                print(res.headers)
                if getattr(res, 'last-modified', None):
                    modified = time.strptime(res.headers['last-modified'], '%a, %d %b %Y %H:%M:%S %Z')
                else:
                    modified = time.localtime()
                if force or modified > self.update_date.timetuple():
                    # need to be re-cached
                    logger.info("Upstream file %s has been updated, time to re-download" % self.url)
                    self.image.save(os.path.basename(self.url), res)
                    
            except urllib.error.HTTPError as e:
                # :shrug:
                logger.debug("Couldn't load %s", self.url)
                logger.debug(str(e))
            self.save()
    
    def get_absolute_url(self):
        return self.image.url
    
    @property
    def stale(self):
        age = timezone.now() - self.update_date
        return age > self.TIMEOUT
    def __unicode__(self):
        return self.url
    __str__ = __unicode__