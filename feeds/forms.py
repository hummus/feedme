import xml.etree.ElementTree
from django import forms


class BookmarkletForm(forms.Form):
    user_id = forms.IntegerField()
    url = forms.URLField()
    title = forms.CharField()
    comment = forms.CharField()


class ImportForm(forms.Form):
    opml = forms.FileField(label="OPML file")

    def clean_opml(self):
        try:
            doc = xml.etree.ElementTree.parse(self.cleaned_data['opml'])
        except xml.etree.ElementTree.ParseError:
            raise forms.ValidationError("Invalid OPML file")

        root = doc.getroot()
        if root.tag != 'opml':
            raise forms.ValidationError("Invalid OPML file")

        return doc
