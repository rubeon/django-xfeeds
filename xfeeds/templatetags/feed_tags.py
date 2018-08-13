from django import template

register = template.Library()

@register.simple_tag
def seen(user, item):
    """
    returns unread items for a user?
    """
    print("---", item.seen_by(user))
    return item.seen_by(user)
