from django.conf import settings

# Number of times module will try to fake an instance
# if unicity constraints are broken because of applying replacers
DJFAKER_MAX_TRIES = getattr(settings, 'DJFAKER_MAX_TRIES', 3)
