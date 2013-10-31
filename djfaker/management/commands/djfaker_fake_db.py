""" Anonymize database for dev or demo instances of a django application """
import sys
from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils.module_loading import module_has_submodule
from django.utils.translation import activate
from django.utils.importlib import import_module
from django.conf import settings

from djfaker.signals import pre_fake_all, post_fake_all
from djfaker import ModelFaker

class Command(BaseCommand):
    """ Django command """
    help = 'Anonymze database for dev or demo instances'
    option_list = BaseCommand.option_list + (
        make_option('--no-deps', action='store_true', dest='no_deps', default=False,
            help='Do not run dependencies'),
        make_option('--no-dels', action='store_true', dest='no_dels', default=False,
            help='Do not run deletions'),
    )
    def handle(self, app=None, no_deps=False, no_dels=False, *args, **options):
        """ Django command handle function ... """

        activate(settings.LANGUAGE_CODE)

        # User could have been selected an app or a ModelFaker directly
        # ex : myapp or myapp.MyModelFaker
        model_given = app and app.find('.') != -1 or False
        if model_given:
            app, model = app.split('.')

        # Autodiscover fakers
        apps = app and [app] or settings.INSTALLED_APPS
        for app in apps:
            mod = import_module(app)
            # Attempt to import the app's fakers module.
            if module_has_submodule(mod, 'fakers'):
                import_module('%s.fakers' % app)

        if model_given:
            faked_models = [getattr(sys.modules.get('%s.fakers' % app), model)]
        else:
            faked_models = ModelFaker.__subclasses__()

        pre_fake_all.send(None, faked_models=faked_models)

        for model_faker in faked_models:
            model_faker()._run(no_deps, no_dels)

        post_fake_all.send(None, faked_models=faked_models)
