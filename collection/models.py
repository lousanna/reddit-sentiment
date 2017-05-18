from __future__ import unicode_literals

from django.db.models import Manager
from django.db import models
from django.db.models.query import QuerySet

class CaseInsensitiveQuerySet(QuerySet):
    def _filter_or_exclude(self, mapper, *args, **kwargs):
        # 'name' is a field in your Model whose lookups you want case-insensitive by default
        if 'name' in kwargs:
            kwargs['name__iexact'] = kwargs['name']
            del kwargs['name']
        return super(CaseInsensitiveQuerySet, self)._filter_or_exclude(mapper, *args, **kwargs)

# custom manager that overrides the initial query set
class CorpManager(Manager):
    def get_query_set(self):
        return CaseInsensitiveQuerySet(self.model)

class Corp(models.Model):
    name = models.CharField(max_length=255,)
    objects = CorpManager()
    def __str__(self):
        return self.name
# Create your models here.
