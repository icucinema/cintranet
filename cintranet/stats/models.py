import collections

from django.db import models

from jsonfield import JSONField


class StatsData(models.Model):
    key = models.CharField(max_length=255)
    value = JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict})
