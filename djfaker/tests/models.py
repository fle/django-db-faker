""" Provides dummy models to fake """
from django.db import models

class FakerTestA(models.Model):
    prop_w = models.CharField(max_length=100, default='foo')
    prop_x = models.CharField(max_length=100, default='bar')
    prop_y = models.CharField(max_length=100, default='oxo')
    old = models.BooleanField(default=False)

class FakerTestB(models.Model):
    prop_z = models.CharField(max_length=100)
