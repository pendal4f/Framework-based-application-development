"""Admin site titles; the homepage app itself has no models."""
from django.contrib import admin

admin.site.site_header = "Места рядом — администрирование"
admin.site.site_title = "Места рядом"
admin.site.index_title = "Управление каталогом и рекомендациями"
