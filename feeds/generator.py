from django.contrib.syndication.views import Feed
from django.utils import feedgenerator

class UserFeed(Feed):

    def get_object(self, request, user_pub_id):
        return get_object_or_404(Beat, pk=utils.decode(user_pub_id))
    
    def items(self, obj):
        return Entry.objects.filter(userentry__user=obj,
                             userentry__shared=True).order_by().order_by('-published')[:30]
    def title(self, obj):
        return "%s's %s shares" %(str(obj),'public')

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return "Crimes recently reported in police beat %s" % obj.beat