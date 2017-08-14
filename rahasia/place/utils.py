from django.contrib.gis.db import models

class Thing(models.Model):
    objects = models.GeoManager()
    point = models.PointField(srid=4326)

    def latitude(self):
        return self.point.y

    def longitude(self):
        return self.point.x