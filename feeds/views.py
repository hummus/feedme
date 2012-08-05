from django.core.urlresolvers import reverse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import RequestSite
from django.utils.encoding import smart_str
from django.http import HttpResponse

from feedme.ajax import json_response
from feedme.utils import validate_url
from feedme.feeds.models import Feed, Entry, UserEntry, EntrySet
from feedme.feeds.forms import ImportForm,BookmarkletForm
from feedme.feeds.tasks import refresh_feeds

from uuid import uuid5,NAMESPACE_URL

import datetime

PUBLIC_NAMED_SETS = {'ALL_SHARED': EntrySet(user_ids=[EntrySet.ALL], 
                                            feed_ids=[EntrySet.ALL], 
                                            qualifiers={'shared':True})}

##
# an internal "feed" just returns a list of entries
# it can really be any of the following:
#  - an individual(website or blog) RSS/AtomFeed that was added 
#           = feed(feed_id).all_entries
#           ~ when feed_id not None
#  - a single user's shared feed 
#           = user_entries(user_id).shared=True
#           ~ when user_id not None
#  - a specific user's overall feed
#           = user(user_id).feeds.all_entries + [each(user.friends).user_entries.shared=True]
#           (sort by published descending) []=not yet implemented
#           ~ when request.user.id = user_id 
#  - the overall public feed for the whole site 
#           = each(user).user_entries.shared=True
#           ~ when feed_id and user_id are None
#TODO:
#  - allow (folder/tag/context/aspect) id?
#  *also allow users to only show their unread entries
###

def label_feed(request, label_name, unread=False):
    #if request.user.is_authenticated:
    import pdb; pdb.set_trace()
    try:
        entries = request.user.get_profile().get_entries_for(label_name)
    except:
        entry_set = PUBLIC_NAMED_SETS.get(label_name,None)
        if not entry_set:
            entries = Entry.objects.none()
        else:
            entries = Entry.objects.filter(**entry_set.get_filter_kwargs())
    
    heading = label_name

    return render(request, 'feeds/feed.html', {
        'heading': heading,
        'entries': entries,
    })

def user_feed(request, user_id, unread=False):
    get_user = get_object_or_404(User, pk=user_id) 

    entries = Entry.objects.filter(userentry__user=get_user,
                                    userentry__shared=True)
    heading = get_user.username

    return render(request, 'feeds/feed.html', {
        'heading': heading,
        'entries': entries,
    })

def feed_feed(request, feed_id=None, unread=False):
    
    feed = get_object_or_404(Feed, pk=feed_id)

    entries = feed.entries
    heading = feed.title
    
    if request.user.is_authenticated():
        if unread:
            entries = entries.exclude(userentry__user=request.user,
                                      userentry__read=True)

        subscribed = request.user.feeds.filter(pk=feed.id).exists()

    else:
        subscribed = None

    entries = entries.all()
    return render(request, 'feeds/feed.html', {
        'heading': heading,
        'entries': entries,
    })


def bookmarklet(request, user_id):

    external_share_url = request.build_absolute_uri( reverse("external_share") )
    
    return render(request, 'feeds/bookmarklet.js', 
                  {
                  'user_id':user_id,
                  'external_share_url':external_share_url
                  },content_type="application/javascript"
                  )

def user_shares(request, user_id=None, unread=True):
    if (user_id):
        return redirect('feed', user_id=user_id)
    
    entries = Entry.objects.filter(userentry__shared=True)
    if request.user.is_authenticated():
        entries = entries.exclude(userentry__user=request.user)
    return render(request, 'feeds/shares.html', {'entries': entries})
    


def home(request):
    bm_initial_url=None
    user_counts=None
    feed_counts=None
    if request.user.is_authenticated():
        user_id = request.user.id
        bm_initial_url = """javascript:(function(){document.body.appendChild(document.createElement('script')).src='"""
        bm_initial_url +="http://%s%s"%(RequestSite(request).domain, reverse("bookmarklet", args=(user_id,)) )
        bm_initial_url +="""';})();"""
        
    return render(request, 'feeds/home.html', 
                  {
                   'bm_initial_url':bm_initial_url,
                  }
           )

@login_required
@require_POST
def subscribe(request, feed_id):
    feed = get_object_or_404(Feed, pk=feed_id)
    request.user.feeds.add(feed)
    return redirect('feed', feed_id=feed.id)


@login_required
@require_POST
def unsubscribe(request, feed_id):
    feed = get_object_or_404(Feed, pk=feed_id)
    request.user.feeds.remove(feed)
    return redirect('feed', feed_id=feed.id)


@login_required
@require_POST
def read(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    user_entry, created = UserEntry.objects.get_or_create(user=request.user,
                                                          entry=entry)
    user_entry.read = True
    user_entry.save()
    if request.is_ajax():
        return json_response({'success': True})
    return redirect('feed', feed_id=entry.feed.id)


@login_required
@require_POST
def share(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    user_entry, created = UserEntry.objects.get_or_create(user=request.user,
                                                          entry=entry)
    user_entry.shared = True
    user_entry.save()
    if request.is_ajax():
        return json_response({'success': True})
    return redirect('feed', feed_id=entry.feed.id)

@csrf_exempt
def external_share(request):
    print request.POST
    if request.method == 'POST':
        form = BookmarkletForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.get(id__exact=form.cleaned_data['user_id'])
            url = form.cleaned_data['url']
            title = form.cleaned_data['title']
            comment = form.cleaned_data['comment']

            #standardize url and use for uuid
            url = validate_url(url)

            #this only wants bytestrs
            uuid = uuid5(NAMESPACE_URL, smart_str(url))
            
            try:
                entry = Entry.objects.get(uuid=uuid)
            except Entry.DoesNotExist:
                entry = Entry()
                entry.feed = None
                entry.uuid = uuid
            
            entry.link = url
            entry.title = title
            #temporarily use comment for content
            entry.content = comment            
            entry.published = datetime.date.today()
            entry.save()

            user_entry = UserEntry()
            user_entry.entry = entry
            user_entry.user = user
            user_entry.shared = True
            user_entry.read = True
            user_entry.save()
            return HttpResponse("saved")

@login_required
def import_opml(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.cleaned_data['opml']
            for el in doc.iterfind('//outline[@type="rss"]'):
                try:
                    feed = Feed.objects.get(uri=el.attrib['xmlUrl'])
                except Feed.DoesNotExist:
                    feed = Feed()
                    feed.uri = el.attrib['xmlUrl']
                    feed.title = el.attrib['text']
                    feed.save()
                request.user.feeds.add(feed)
            refresh_feeds()
            return redirect('home')
    else:
        form = ImportForm()
    return render(request, 'feeds/import_opml.html', {'form': form})
