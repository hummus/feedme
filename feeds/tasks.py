import time
import datetime
import HTMLParser
import feedparser
import logging

from feedme.feeds.models import Feed, Entry
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

logger = logging.getLogger(__name__)

# class failsafe_task(object):
#     def __init__(self, *args, **kw_args):
#         self.kwargs = kw_args

#     def __call__(self, task, **kwargs):
#         p = Process(target=task, kwargs=self.kwargs)
#         p.start()



try:
    from celery.task import task
except:
    from multiprocessing import Process
    from functools import wraps
    def task(func):
        logger.debug(str(func))
        @wraps(func)
        def run(*args, **kwargs):
            p = Process(target=func, args=args, kwargs=kwargs)
            p.start()
            return lambda x: x
        return run


@task#(ignore_result=True)
def refresh_feeds():
    for feed_id in Feed.objects.values_list('id', flat=True):
        refresh_feed.subtask().delay(feed_id)

#@receiver(user_logged_in)
#@task(ignore_result=True)
#def refresh_user_feeds(send, user, request):
#    for feed_id in Feed.objects.filter(users__pk=user.id):
#        refresh_feed.subtask().delay(feed_id)


@task#(ignore_result=True)
def refresh_feed(feed_id):
    # Used to unescape html entities in titles    
    html_parser = HTMLParser.HTMLParser()
    feed = Feed.objects.get(pk=feed_id)
    parsed = feedparser.parse(feed.uri)

    #import pdb; pdb.set_trace()
    if parsed.bozo:
        logger.warning('feedparser got bozo error. skipping feed')
        return

    parsed_feed = parsed.feed
    title = parsed_feed.title if hasattr(parsed_feed,'title') else feed.uri
    feed.title = html_parser.unescape(title)
    feed.save()

    for parsed_entry in parsed.entries:
        uuid = getattr(parsed_entry, 'id', parsed_entry.link)

        try:
            entry = Entry.objects.get(uuid=uuid)
        except Entry.DoesNotExist:
            entry = Entry()
            entry.feed = feed
            entry.uuid = uuid

        entry.link = parsed_entry.link
        entry.title = html_parser.unescape(parsed_entry.title)
        entry.author = getattr(parsed_entry, 'author', None)

        timestamp = time.mktime(parsed_entry.updated_parsed)
        entry.published = datetime.datetime.fromtimestamp(timestamp)

        if hasattr(parsed_entry, 'content'):
            entry.content = parsed_entry.content[0].value
        elif hasattr(parsed_entry, 'summary'):
            entry.content = parsed_entry.summary

        entry.save()
