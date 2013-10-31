from django.conf import settings

# Number of times module will try to faker an instance if unicity constraints are broken
# becaus of applying replacers
FAKER_MAX_TRIES = getattr(settings, 'FAKER_MAX_TRIES', 3)
