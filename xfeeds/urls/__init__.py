from django.conf.urls import url
from django.conf.urls import include
from ..views import feed
urlpatterns = [
    url(r'feed/$', feed.FeedListView.as_view(paginate_by=1), name="feed-list"),
    url(r'feed/(?P<pk>\d+)$', feed.FeedDetailView.as_view(), name="feed-detail"),
    url(r'feed/add/$', feed.FeedCreateView.as_view(), name="feed-add"),
    url(r'feed/update/(?P<pk>\d+)$', feed.FeedEditView.as_view(), name="feed-update"),
    url(r'all/$', feed.FeedItemListView.as_view(paginate_by=50), name="feeditem-list"),
    url(r'feeditem/(?P<pk>\d+)$', feed.FeedItemDetailView.as_view(), name="feeditem-detail"),
    ]
