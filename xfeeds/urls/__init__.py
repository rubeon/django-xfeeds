from django.conf.urls import url
from django.urls import path
# from django.conf.urls import include
from ..views import feed
urlpatterns = [
    # url(r'feed/$', feed.FeedListView.as_view(paginate_by=1), name="feed-list"),
    
    # url(r'feed/add/$', feed.FeedCreateView.as_view(), name="feed-add"),
    # url(r'feed/add/lookup_feeds$', feed.list_feeds_url, name="feed-add"),
    # url(r'feed/update/(?P<pk>\d+)$', feed.FeedEditView.as_view(), name="feed-update"),
    # url(r'all/$', feed.FeedItemListView.as_view(paginate_by=50), name="feeditem-list"),
    path('feed/<int:pk>', feed.FeedDetailView.as_view(), name="feed-detail"),
    path('feeditem/<int:pk>', feed.FeedItemDetailView.as_view(), name='feeditem-detail'),
    path('', feed.FeedItemListView.as_view(paginate_by=20), name='feed-list'),
    ]

__all__ = [urlpatterns,]