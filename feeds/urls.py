from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns(
    'feedme.feeds.views',
    
    url(r'^import/', 'import_opml', name='import'),

    #feed-related
    url(r'^$', 'home', name='home'),
        
    # TODO greader uses full url for actual feeds, is this better?
    url(r'^feed/(?P<feed_id>\d+)/$', 'feed_feed', name='feed'),
    #url(r'^feed/(?P<feed_id>\d+)/all/$', 'feed_feed', kwargs={'unread': False}),
    
    url(r'^user/(?P<user_id>\w+)/$', 'user_feed'),
    url(r'^user_feed/(?P<user_id>\w+)/$', 'user_feed', name='user'),

    url(r'^label/(?P<label_name>\w+)/$', 'label_feed', name='label'),
    
    # User feed views
    url(r'^subscribe/(?P<feed_id>\d+)/$', 'subscribe', name='subscribe'),
    url(r'^unsubscribe/(?P<feed_id>\d+)/$', 'unsubscribe', name='unsubscribe'),

    # User entry views
    url(r'^refresh_feed/(?P<feed_id>\d+)/$', 'refresh_feed', name='refresh_feed'),
    url(r'^read/(?P<entry_id>\d+)/$', 'read', name='read'),
    url(r'^share/(?P<entry_id>\d+)/$', 'share', name='share'),
    
    url(r'^external_share/$','external_share', name='external_share'),
    url(r'^bookmarklet/(?P<user_id>\d+)/$','bookmarklet', name='bookmarklet'),

    #public feeds
    #url(r'^rss/$', 'shares', name='shares'),
    #url(r'^rss/(?P<user_pub_id>\d+)/$', 'shares', name='shares'),
    #url(r'^shares/(?P<user_pub_id>\d+)/(?P<user_aspect_id>$', 'shares', name='shares'),
)
