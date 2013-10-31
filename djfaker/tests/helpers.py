""" Some helpers for testing  """
from django.core.management import call_command
from django.conf import settings
from django.db.models import loading
from django.test import TestCase
from .fakers import FakerTestAFaker, FakerTestBFaker

class FakerBaseTest(TestCase):

    def _pre_setup(self):
        self.old_installed_apps = settings.INSTALLED_APPS
        settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)
        settings.INSTALLED_APPS.append('djfaker.tests')
        loading.cache.loaded = False
        call_command('syncdb', verbosity=0)
        super(FakerBaseTest, self)._pre_setup()

    def setUp(self):
        super(FakerBaseTest, self).setUp()
        FakerTestBFaker._ran = False
        FakerTestAFaker._ran = False

    def _post_teardown(self):
        settings.INSTALLED_APPS = self.old_installed_apps
        super(FakerBaseTest, self)._post_teardown()
