from django.forms import ModelForm

from collection.models import Corp

class CorpForm(ModelForm):
    class Meta:
        model = Corp
        fields = ('name', )
        labels = {
            "name":"Company name"
        }
