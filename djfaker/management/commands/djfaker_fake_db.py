""" Anonymize database for dev or demo instances of a django application """
import sys
from optparse import make_option

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.utils.module_loading import module_has_submodule
from django.utils.translation import activate
from django.utils.importlib import import_module
from django.conf import settings

from djfaker.signals import pre_fake_all, post_fake_all
from djfaker import ModelFaker


def autodiscover_models(given_app=None, given_model=None):
    """ Autodiscover `fakers` modules and `ModelFaker` subclasses
        `given_app` can be given to restrict autodiscovering
        `given_model` can be given to fake only one model
    """

    if given_model and not given_app:
        raise ImproperlyConfigured("If model is given, app must be given too ")

    # Autodiscover fakers
    apps = given_app and [given_app] or settings.INSTALLED_APPS
    for app in apps:
        mod = import_module(app)
        # Attempt to import the app's fakers module.
        if module_has_submodule(mod, 'fakers'):
            import_module('%s.fakers' % app)

    models = ModelFaker.__subclasses__()
    if given_app:
        module_fakers = getattr(sys.modules.get(given_app), 'fakers')
        models = [m for m in models
                  if m.__module__.startswith(module_fakers.__name__)]
        if given_model:
            models = [getattr(module_fakers, given_model)]

    return models


class Command(BaseCommand):
    """ Django command """
    help = 'Anonymze database for dev or demo instances'
    option_list = BaseCommand.option_list + (
        make_option(
            '--no-deps', action='store_true', dest='no_deps', default=False,
            help='Do not run dependencies'),
        make_option(
            '--no-dels', action='store_true', dest='no_dels', default=False,
            help='Do not run deletions'),
    )

    def handle(self, app=None, model=None, no_deps=False, no_dels=False,
               *args, **options):
        """ Django command handle function ... """

        activate(settings.LANGUAGE_CODE)

        faked_models = autodiscover_models(app, model)
        pre_fake_all.send(None, faked_models=faked_models)

        for model_faker in faked_models:
            model_faker()._run(no_deps, no_dels)

        post_fake_all.send(None, faked_models=faked_models)
