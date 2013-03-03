#from util import admin
from django.contrib import admin
from smartdbstorage.models import DBFile


class DBFileAdmin(admin.ModelAdmin):
    list_filter = ('pool', )
    list_display = ('pool', 'view', 'name', 'created_at', 'updated_at')
    search_fields = ['name']

    def view(self, obj):
        return '<a href="%s">Open</a>' % obj.get_absolute_url()
    view.allow_tags = True

admin.site.register(DBFile, DBFileAdmin)
