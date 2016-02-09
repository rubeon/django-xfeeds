from django.http import HttpResponse
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse_lazy

from ..models.feed import FeedItem
from ..models.feed import Feed
from ..models.tag import SeenItem

from ..parser import tasks

from logging import getLogger
logger = getLogger(__name__)

class FeedItemListView(ListView):
    model = FeedItem
    
class FeedItemDetailView(DetailView):
    model = FeedItem
    def get(self, *args, **kwargs):
        # mark this as read
        obj = self.get_object()
        if self.request.user.is_authenticated():
            logger.info("Marking %s read for %s" % (obj, self.request.user))
            si = SeenItem(content_object=obj, user=self.request.user)
            si.save()
        return super(self.__class__, self).get(self, *args, **kwargs)
    
class FeedListView(ListView):
    model = Feed
    
    def get_context_data(self, *args, **kwargs):
        logger.debug("%s.%s.get_context_data entered" % (__name__, self))
        context = super(self.__class__, self).get_context_data(*args, **kwargs)
        print type(context)
        # make a queryset for seen items
        if self.request.user.is_authenticated():
            seen_items = [si.content_object for si in SeenItem.objects.filter(user=self.request.user)]
        else:
            # FIXME: this can be put into session data, HTML database, etc.
            seen_items = []
            
        logger.debug( "-- %s" % seen_items)
        context['seen_items']=seen_items
        return context

class FeedDetailView(DetailView):
    model = Feed
    # template_name = "xfeeds/feed_list.html"
    
    def get_context_data(self, *args, **kwargs):
        context = super(self.__class__, self).get_context_data(*args, **kwargs)
        print type(context)
        # make a queryset for seen items
        seen_items = [si.content_object for si in SeenItem.objects.filter(user=self.request.user)]
        # user = self.request.user
        # if user.is_authenticated:
        #     read_items = self.model.feeditems_set.seen_by(user=user)
        # else:
        #     read_items = ['a','b','c']
        # context['unread_items']=unread_items
        print "--", seen_items
        context['seen_items']=seen_items
        return context
        
class FeedCreateView(CreateView):
    model = Feed
    fields = ['feed_url']
    success_url = reverse_lazy('xfeeds:feed-detail')    
    def form_valid(self, form):
        form.instance = tasks.url_to_feed(form.instance.feed_url)
        self.object = form.instance
        return super(self.__class__, self).form_valid(form)
    
    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("xfeeds:feed-detail", kwargs={'pk':self.object.pk })
        
class FeedEditView(UpdateView):
    model = Feed
    fields = ['feed_title', 'feed_url', 'is_active']
    success_url = reverse_lazy('xfeeds:feed-list')
    
    def form_valid(self, form):
        # update the feed items on this feed
        tasks.update_items(form.instance)
        return super(self.__class__, self).form_valid(form)