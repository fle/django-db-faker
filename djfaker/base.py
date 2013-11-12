from django.utils.importlib import import_module
from django.core.exceptions import ValidationError, ImproperlyConfigured

from .exceptions import FakerUnicityError
from .replacers import BaseReplacer, SimpleReplacer, LazyReplacer
from .signals import pre_fake_model, post_fake_model
from .settings import DJFAKER_MAX_TRIES

# Special declarations
FAKER_DECLARATIONS = [
    'FAKER_FOR', 'QS_FOR_DELETION', 'QS_FOR_UPDATE', 'DEPENDS_ON']


class ModelFaker(object):

    # Django model class you wan to fake
    FAKER_FOR = None

    # Lambda : Queryset selecting instances you want to simply delete
    QS_FOR_DELETION = None

    # Lambda : Queryset selecting instances you want to fake
    # if None, all instances will be faked
    QS_FOR_UPDATE = None

    # Which fakers (ModelFaker subclasses) should be run before this one
    DEPENDS_ON = []

    # Internal utility : set to True when this faker is ran
    _ran = False

    def _get_replacers(self, replacerClass=None):
        """ Returns declared replacers that will be applied on instances.
            if `replacerClass` is None, returns simple builtin values
            if `replacerClass` is given, returns subclasses of `replacerClass`
        """
        attrs = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if attr_name in FAKER_DECLARATIONS or attr_name.startswith('_'):
                # Skip special declarations and native python attributes
                continue
            if not replacerClass and not issubclass(type(attr), BaseReplacer):
                # Not a *Replacer class, just a builtin value (int, bool, ...)
                attrs.append(attr_name)
            elif replacerClass and issubclass(type(attr), replacerClass):
                # faker.replacer.*Replacer attribute
                attrs.append(attr_name)
        return attrs

    @classmethod
    def _validate(cls):
        """ Ensures that ModelFaker is well configured """
        if not cls.FAKER_FOR:
            raise ImproperlyConfigured()
        if cls.QS_FOR_DELETION and not hasattr(cls.QS_FOR_DELETION, '__call__'):
            raise ImproperlyConfigured()
        if cls.QS_FOR_UPDATE and not hasattr(cls.QS_FOR_UPDATE, '__call__'):
            raise ImproperlyConfigured()

    @classmethod
    def _run_dependencies(cls):
        """ Runs dependencies declared in cls.DEPENDS_ON """
        for dependency in cls.DEPENDS_ON:
            app, module, klass = dependency.rsplit('.', 2)
            import_module(app)
            fakers = import_module('%s.fakers' % app)
            #print cls, " need dependency ", klass
            getattr(fakers, klass)()._run()

    def _run_deletion(self):
        """ Deletes instances selected by cls.QS_FOR_DELETION """
        if self.QS_FOR_DELETION:
            self.QS_FOR_DELETION().delete()

    def _get_update_qs(self):
        """ Returns queryset that selects instances to be faked (updated) """
        if self.QS_FOR_UPDATE:
            qs = self.QS_FOR_UPDATE()
        else:
            qs = self.FAKER_FOR.objects.all()
        return qs

    def _run_update(self):
        """ Fakes instances by applying declared replacers """
        cls = self.__class__

        # Simple builtin values
        native_attrs = self._get_replacers()
        # Replacers which are not dependent of the instance other fields
        simple_attrs = self._get_replacers(SimpleReplacer)
        # Replacers which can be dependent of the instance other fields
        lazy_attrs = self._get_replacers(LazyReplacer)

        if not any([native_attrs, simple_attrs, lazy_attrs]):
            # Nothing to do !
            return

        qs = self._get_update_qs()
        for instance in qs:

            """
            Dumb validation methods : Faking data can generate unicity error
            Algorithm is :
            - Apply replacers on an instance
            - Run validate_unique()
                - If OK : save instance and go forward
                - If ValidationError is raised : retry !
            DJFAKER_MAX_TRIES limits number of tries and raises a
            FakerUnicityError if it is reached
            """
            tries = 0
            while tries <= DJFAKER_MAX_TRIES:

                for attr in native_attrs:
                    replacer = getattr(cls, attr)
                    setattr(instance, attr, replacer)

                for attr in simple_attrs:
                    replacer = getattr(cls, attr)
                    setattr(instance, attr, replacer.apply())

                for attr in lazy_attrs:
                    replacer = getattr(cls, attr)
                    setattr(instance, attr, replacer.apply(instance))

                try:
                    instance.validate_unique()
                except ValidationError, e:
                    tries += 1
                    if DJFAKER_MAX_TRIES == tries:
                        raise FakerUnicityError(e.message_dict.keys())
                else:
                    instance.save()
                    break

    def _run(self, no_deps=False, no_dels=False):
        """ Main method which orchestrates faking of a model instances """
        cls = self.__class__

        if cls._ran:
            #print "Already ran ", cls
            return

        pre_fake_model.send(None, faked_model=cls)
        #print "Run ", cls

        cls._validate()

        if not no_deps:
            cls._run_dependencies()

        if not no_dels:
            self._run_deletion()

        self._run_update()

        post_fake_model.send(None, faked_model=cls)
        #print "Ran ", cls
        cls._ran = True
