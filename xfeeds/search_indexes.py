import datetime
from haystack import indexes
from .models import FeedItem

class FeedItemIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='author')
    pub_date = indexes.DateTimeField(model_attr='pubDate')
    title = indexes.CharField(model_attr='title')

    def get_model(self):
        return FeedItem

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
