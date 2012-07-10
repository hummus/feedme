"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from feedme.feeds.models import Entry

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

# class BookmarkletTest(TestCase):
# 	def test_unattached_entry:
#         entry = Entry()
#         entry.feed = None
#         entry.content = 'asdfadf'
#         entry.uuid = 
#         entry.link = url
#         entry.title = title
#         entry.published = datetime.date.today()
#         entry.save()
#         user_entry = UserEntry()
#         user_entry.user = user

