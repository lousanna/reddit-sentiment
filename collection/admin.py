from django.contrib import admin

from collection.models import Corp

class CorpAdmin(admin.ModelAdmin):
    model = Corp
    list_display = ('name', )
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Corp)
# Register your models here.
