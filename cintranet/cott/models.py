from django.db import models

import ticketing.models

class AuthenticationCredential(models.Model):
    auth_slug = models.SlugField(null=False, blank=False)
    auth_data = models.TextField(null=False, blank=False)

class Product(models.Model):
    org_id = models.PositiveSmallIntegerField(null=True, blank=True)
    eactivities_id = models.PositiveSmallIntegerField(null=True, blank=True)
    name = models.CharField(max_length=256, null=False, blank=True)
    sold = models.PositiveSmallIntegerField(null=True, blank=True)
    initial = models.PositiveSmallIntegerField(null=True, blank=True)

class SKU(models.Model):
    product = models.ForeignKey(Product)
    eactivities_id = models.PositiveSmallIntegerField(null=True, blank=True)
    name = models.CharField(max_length=256, null=False, blank=False)
    sold = models.PositiveSmallIntegerField(null=True, blank=True)
    initial = models.PositiveSmallIntegerField(null=True, blank=True)
    dirty = models.BooleanField(null=False, default=False)

class SKUEntitlement(models.Model):
    sku = models.ForeignKey(SKU)
    entitlement = models.ForeignKey(ticketing.models.Entitlement)
    uses_remaining = models.PositiveSmallIntegerField(null=True, blank=True)
