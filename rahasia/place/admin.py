from django.contrib.gis import admin
from place.models import Place

admin.site.register(Place, admin.OSMGeoAdmin)
# Register your models here.
#admin.site.register(Place)