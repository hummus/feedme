from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns(
    'feedme.feeds.views',
    
    url(r'^import/', 'import_opml', name='import'),

    #feed-related
    url(r'^$', 'home', name='home'),
    url(r'^me$', 'home', name='feed'),
    # TODO greader uses full url for actual feeds, is this better?
    url(r'^feed/(?P<feed_id>\d+)/$', 'feed', name='feed'),
    url(r'^feed/(?P<feed_id>\d+)/all/$', 'feed', kwargs={'unread': False}),
    
    # U
    url(r'^user/(?P<username>\d+)/$', 'feed', name='user_feed'),
    
    # User feed views
    url(r'^subscribe/(?P<feed_id>\d+)/$', 'subscribe', name='subscribe'),
    url(r'^unsubscribe/(?P<feed_id>\d+)/$', 'unsubscribe', name='unsubscribe'),

    # User entry views
    url(r'^read/(?P<entry_id>\d+)/$', 'read', name='read'),
    url(r'^share/(?P<entry_id>\d+)/$', 'share', name='share'),
    
    url(r'^external_share/$','external_share', name='external_share'),
    url(r'^bookmarklet/(?P<user_id>\d+)/$','bookmarklet', name='bookmarklet'),

    #public feeds
    url(r'^rss/$', 'shares', name='shares'),
    url(r'^rss/(?P<user_pub_id>\d+)/$', 'shares', name='shares'),
    #url(r'^shares/(?P<user_pub_id>\d+)/(?P<user_aspect_id>$', 'shares', name='shares'),
)
