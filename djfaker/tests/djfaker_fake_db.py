""" Test djfaker_fake_db command """
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command

from djfaker.management.commands.djfaker_fake_db import autodiscover_models

from .helpers import FakerBaseTest
from .testapp.fakers import FakerTestAFaker, FakerTestBFaker
from .testapp2.fakers import DummyEmptyFaker


class DJFakerFakeDBTest(FakerBaseTest):
    """ Test djfaker_fake_db command """

    def test_autodiscover_models(self):
        """ Test autodiscover_models function """

        # Without app
        models = autodiscover_models()
        self.assertIn(FakerTestAFaker, models)
        self.assertIn(FakerTestBFaker, models)
        self.assertIn(DummyEmptyFaker, models)

        # With app
        models = autodiscover_models('djfaker.tests.testapp')
        self.assertIn(FakerTestAFaker, models)
        self.assertIn(FakerTestBFaker, models)
        self.assertNotIn(DummyEmptyFaker, models)

        # With app and model
        models = autodiscover_models('djfaker.tests.testapp', 'FakerTestAFaker')
        self.assertIn(FakerTestAFaker, models)
        self.assertNotIn(FakerTestBFaker, models)
        self.assertNotIn(DummyEmptyFaker, models)

        # Invalid call
        self.assertRaises(ImproperlyConfigured,
                          autodiscover_models, None, 'FakerTestAFaker')

    def test_command(self):
        """ Test a real command call """
        call_command('djfaker_fake_db',
                     app='djfaker.tests.testapp',
                     model='FakerTestAFaker')
        self.assertTrue(FakerTestAFaker._ran)
        self.assertTrue(FakerTestBFaker._ran)
