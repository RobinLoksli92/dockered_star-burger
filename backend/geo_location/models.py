from django.db import models

from django.utils import timezone


class GeoLocation(models.Model):
    address = models.CharField('Адрес', max_length=200, unique=True)
    lat = models.DecimalField('Широта', max_digits=10, decimal_places=5, null=True)
    long = models.DecimalField('Долгота', max_digits=10, decimal_places=5, null=True)
    request_date = models.DateTimeField('Дата запроса к геокодеру', default=timezone.now)

    def __str__(self):
        return self.address

