"""
Faker-specific signals
"""
from django.dispatch import Signal
from django.conf import settings


# Sent before faking of a model
pre_fake_model = Signal(providing_args=["faked_model"])

# Sent after faking of a model
post_fake_model = Signal(providing_args=["faked_model"])

# Sent before global faking of all apps
pre_fake_all = Signal(providing_args=["faked_models"])

# Sent after global faking of all apps
post_fake_all = Signal(providing_args=["faked_models"])
