""" fakers.py file for dummy models of our test app """
from . import models
from djfaker import replacers, ModelFaker


class FakerTestAFaker(ModelFaker):
    """ Faker for FakerTestA model """
    FAKER_FOR = models.FakerTestA
    QS_FOR_DELETION = lambda x: models.FakerTestA.objects.filter(old=True)
    QS_FOR_UPDATE = lambda x: models.FakerTestA.objects.filter(prop_w='foo')
    DEPENDS_ON = ('djfaker.tests.testapp.fakers.FakerTestBFaker', )

    # Faked by replacing by a constant builtin value (a.k.a "native replacer")
    prop_w = 'dummyA'
    # Faked by applying a "simple replacer"
    prop_x = replacers.ChoiceReplacer(choices=['Jack'])
    # Faked by applying a "lazy replacer"
    prop_y = replacers.TextReplacer(tpl='Hello {0}', tokens=['prop_x'])


class FakerTestBFaker(ModelFaker):
    """ Faker for FakerTestB model """
    FAKER_FOR = models.FakerTestB

    prop_z = 'dummyB'


class DummyFakerWithoutDeletionQS(ModelFaker):
    """ A dummy faker to test behavior when QS_FOR_DELETION is not provided """
    FAKER_FOR = models.FakerTestA


class DummyFakerWithoutUpdateQS(ModelFaker):
    """ A dummy faker to test behavior when QS_FOR_DELETION is not provided """
    FAKER_FOR = models.FakerTestA


class DummyFakerWithoutReplacers(ModelFaker):
    """ A dummy faker to test behavior when no replacer is not provided """
    FAKER_FOR = models.FakerTestA


class DummyInvalidFaker1(ModelFaker):
    """ A dummy invalid faker because it does not provide FAKER_FOR """
    pass


class DummyInvalidFaker2(ModelFaker):
    """ A dummy invalid faker because QS_FOR_DELETION is not a callable """
    FAKER_FOR = models.FakerTestA
    QS_FOR_DELETION = 'foo'


class DummyInvalidFaker3(ModelFaker):
    """ A dummy invalid faker because QS_FOR_UPDATE is not a callable """
    FAKER_FOR = models.FakerTestA
    QS_FOR_UPDATE = 'foo'
