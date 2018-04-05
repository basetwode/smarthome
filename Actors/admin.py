from django.contrib import admin

# Register your models here.
from Actors.models import LEDActor, Configuration

admin.site.register(LEDActor)
admin.site.register(Configuration)