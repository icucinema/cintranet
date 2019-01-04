from django.db import models
import collections
#from jsonfield import JSONField
from django.contrib.postgres.fields import JSONField

class StatsData(models.Model):
    key = models.CharField(max_length=255)
    value = JSONField()

    def __str__(self):
        return self.key

    class Meta:
        verbose_name = "stats datum"
        verbose_name_plural = "stats data"
