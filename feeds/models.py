from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


#maybe should be recursive?
class EntrySet():
    ALL = -1

    def __init__(self, feed_ids=[], user_ids=[], qualifiers={}):
        '''
        params:
        qualifier_list=dict of userentry boolean fields to select/deselect for
        '''
        self.feed_ids = feed_ids
        self.user_ids = user_ids
        self.qualifiers = qualifiers

    def get_filter_kwargs(self):
        kw = {}
        if self.user_ids and not EntrySet.ALL in self.user_ids:
            kw.update({'userentry__user__in':self.user_id_list})
        
        if self.feed_ids and not EntrySet.ALL in self.feed_ids:
            kw.update({'feed_id__in':self.feed_id_list})
        
        if self.qualifiers:
            for (q,b) in self.qualifiers.iteritems():
                print q,b
                kw.update({'userentry__%s'%q:b})
        return kw




class Feed(models.Model):
    uri = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255, blank=True)
    users = models.ManyToManyField(User, related_name='feeds')
    # enabled = models.BooleanField(default=True)
    # last_checked = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        ordering = ('title',)

    def __unicode__(self):
        return self.title

    def clean(self):
        if not self.title:
            self.title = self.uri
        super(Feed, self).clean()


class Entry(models.Model):
    feed = models.ForeignKey('Feed', related_name='entries', null=True, blank=True, default=None)
    uuid = models.CharField(max_length=255, unique=True)
    link = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, null=True, blank=True)
    published = models.DateTimeField()
    content = models.TextField(null=True, blank=True)
    users = models.ManyToManyField(User,
                                   related_name='entries',
                                   through='UserEntry')

    class Meta:
        ordering = ('-published',)

    def __unicode__(self):
        return self.title

class UserEntry(models.Model):
    user = models.ForeignKey(User)
    entry = models.ForeignKey('Entry')
    read = models.BooleanField(default=False)
    bookmarked = models.BooleanField(default=False)
    shared = models.BooleanField(default=False)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    #include_read = models.BooleanField(default=True)
    #friends = models.ForeignKey(User)
    
    def __str__(self):  
          return "%s's profile" % self.user
      
    def unread(self, user=None, feed=None):
        if user:
            user_shared_entries = Entry.objects.filter(
                                                       userentry__user_id=user.id,
                                                       userentry__shared=True
                                                       ).values_list('id',flat=True)
            
            unread_count = Entry.objects.filter(
                                                      id in user_shared_entries,
                                                      userentry__user_id=self.user.id,
                                                      userentry__read=True
                                                    ).count()
            return unread_count
        elif feed:
            unread_entries = Entry.objects.filter(feed_id=feed_id)
            unread_count = unread_entries.exclude(
                                                  userentry__user_id=self.user.id,
                                                  userentry__read=True,
                                                 ).count()
            return unread_count 
        else: 
            return None
    
    def get_entries_for(setname):
        entries = None
        #these are specific for a user
        if setname=='READING':
            es = EntrySet(user_ids=[self.user.id], 
                            feed_ids=[EntrySet.ALL])
            entries = Entry.objects.filter(**es.get_filter_kwargs())
        
        if setname=='SHARING':
            es =  EntrySet(user_ids=[self.user.id],
                            feed_ids=[EntrySet.ALL],
                            qualifiers={'shared':True})
            entries = Entry.objects.filter(**es.get_filter_kwargs())
        if setname=='ALL_SHARED':
            es = EntrySet(user_ids=[EntrySet.ALL],
                            feed_ids=[EntrySet.ALL],
                            qualifiers={'shared':True})
            entries = Entry.objects.filter(**es.get_filter_kwargs()).exclude(userentry__user_id=user.id)

        return entries


#def create_user_profile(sender, instance, created, **kwargs):  
#    if created:  
#        profile, created = UserProfile.objects.get_or_create(user=instance)  
#        
#post_save.connect(create_user_profile, sender=User)
    
