from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponse
from collection.models import Corp
from collection.forms import CorpForm
import os
import chat
from chat import getQuery
from chat import addCompany
from chat import scanComp
from chat import seeComments

def list(request):
    corps = Corp.objects.all()
    corps = getQuery(False)
    return render(request, 'list.html', {
                  'corps': corps,
                  })

def index(request):

    os.chdir(os.path.dirname(__file__))
    # set the form we're using
    form_class = CorpForm
    corps = None
    corp = None
    comments = None
    # if we're coming to this view from a submitted form
    if request.method == 'POST':
        # grab the data from the submitted form and apply to
        # the form
        form = form_class(request.POST)
        if form.is_valid():
            corps = scanComp(form.cleaned_data['name'])
            corp = form.cleaned_data['name']
            comments = seeComments(corp)
    # otherwise just create the form
    else:
        form = form_class()

    # and render the template
    return render(request, 'index.html', {
                  'corps': corps,
                  'form': form,
                  'corp': corp,
                  'comments': comments,
                  }, context_instance=RequestContext(request))

def thing_detail(request, slug):
    lastind = slug.rfind(' : ')
    firstind = slug.find(' ')
    corp = slug[firstind+1:lastind]
    corps = scanComp(corp)
    comments = seeComments(corp)
    
    # and pass to the template
    return render(request, 'thing_detail.html', {
                  'corps': corps,
                  'corp': corp,
                  'comments': comments,
                  })
