# django-xfeeds
A newsfeed reader for your django site.

## Install

Add the following to your settings.INSTALLED_APPS:

```python

    INSTALLED_APPS = [ 
        'xfeeds',
    ]
```

And to your site's `urls.py`:

```python

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reader/', include(('xfeeds.urls', 'xfeeds')), ),
]

```

## Templates

There are several default content blocks in the application:

* `mainconent`: This displays the core content of the XFeeds app.  Feed lists, Feed Items, and whatever else you would expect to be bang in the middle of your page
* `contentnav`: This is a set of includes that you could put to the left or right of the content to provide navigation elements
* `extratitle`: for adding extra bits to the HTML `<title>` tag
* `extraheader`: If you have a header in your navigation, you can place the context in this


## Loading feeds

* Use the `seed` management command in Django using a really ill-behaved spider
* Use the `update_feeds` management command to update all the feeds

```bash

./manage.py seed http://myblog.org/

```

See `./manage.py seed -h` for usage.



## Example Template, using [Bootstrap 4][bootstrap]:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="x-ua-compatible" content="ie=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
  <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>

  <title>{{ request.site.name }}||{%block extratitle %}Home{% endblock %}</title>

  
</head>
<body>
<div class="container" id="wrapper">
    <div class="row">
        <div class="col-4">{{ request.site.name }}||{%block extraheader %}{{ request.user }}{% endblock %}</div>
        <div class="col-8"></div>
    </div>
    <div class="row">
        <div class="col-8">{% block maincontent %}{% endblock %}</div>
        <div class="col-4">{% block contentnav %}{% endblock %}</div>
    </div>

</div>
</body>
</html>
```

[bootstrap]:https://getbootstrap.com/docs/4.0/examples/starter-template/