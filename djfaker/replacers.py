from random import choice, randint, shuffle
from uuid import uuid4
from django.template.defaultfilters import slugify
from django.contrib.auth.hashers import make_password
from . import data


# Base classes -----------------------------------------------------------------


class BaseReplacer(object):
    """ Just a base class used to facilitate autodiscovering of replacers """
    pass


class SimpleReplacer(BaseReplacer):
    """ Replacers which are not dependent of the instance other fields """
    def apply(self):
        raise NotImplementedError


class LazyReplacer(BaseReplacer):
    """ Replacers which are dependent of the instance other fields """
    tokens = []

    def __init__(self, tokens=None):
        if tokens:
            self.tokens = tokens

    def apply(self, instance):
        raise NotImplementedError


# SimpleReplacer subclasses ----------------------------------------------------


class ChoiceReplacer(SimpleReplacer):
    choices = []

    def __init__(self, choices=None):
        if choices:
            self.choices = choices

    def apply(self):
        return choice(self.choices)


class ChoiceUniqueReplacer(SimpleReplacer):
    choices = []
    with_shuffle = False

    def __init__(self, choices=None, with_shuffle=None):
        if choices:
            self.choices = choices
        self.with_shuffle = with_shuffle or self.with_shuffle

    def apply(self):
        if self.with_shuffle:
            shuffle(self.choices)
        ch = self.choices.pop()
        return ch


class CompanyReplacer(SimpleReplacer):
    COMPANIES = data.COMPANIES
    COMPANIES_EXTRA = data.COMPANIES_EXTRA

    def apply(self):
        tpl = choice(['{0} {1}', '{1} {0}'])
        return tpl.format(
            choice(self.COMPANIES),
            choice(self.COMPANIES_EXTRA))


class EmailReplacer(SimpleReplacer):
    LAST_NAMES = data.LAST_NAMES
    FIRST_NAMES = data.FIRST_NAMES
    MAIL_EXTS = data.MAIL_EXTS

    def apply(self):
        return '{0}.{1}@{2}.example.com'.format(
            slugify(choice(self.FIRST_NAMES)),
            slugify(choice(self.LAST_NAMES)),
            choice(self.MAIL_EXTS))


class PhoneReplacer(SimpleReplacer):
    def apply(self):

        return '(+33){0}{1}'.format(
            randint(1, 9),
            randint(10000000, 99999999))


class MobileReplacer(SimpleReplacer):
    def apply(self):
        return '(+33){0}{1}'.format(
            randint(1, 9),
            randint(10000000, 99999999))


class SerialReplacer(SimpleReplacer):
    len = 12
    int_only = False

    def __init__(self, len=None, int_only=None):
        self.len = len or self.len
        self.int_only = int_only or self.int_only

    def apply(self):
        uid = uuid4().hex
        if self.int_only:
            uid = uuid4().int
        return '{0}'.format(uid)[:self.len].upper()


# LazyReplacer subclasses ------------------------------------------------------


class MethodCallbackReplacer(LazyReplacer):
    def apply(self, instance):
        return getattr(instance, self.tokens[0])()


class LazyEmailReplacer(LazyReplacer):
    MAIL_EXTS = data.MAIL_EXTS
    TPL = '{0}.{1}@{2}.example.com'

    def apply(self, instance):
        return self.TPL.format(
            slugify(getattr(instance, self.tokens[0])),
            slugify(getattr(instance, self.tokens[1])),
            choice(self.MAIL_EXTS))


class LazyUsernameReplacer(LazyReplacer):

    def apply(self, instance):
        return '{0}.{1}'.format(
            slugify(getattr(instance, self.tokens[0])),
            slugify(getattr(instance, self.tokens[1])))


class LazyPasswordReplacer(LazyReplacer):

    def apply(self, instance):
        raw_password = '{0}{1}'.format(
            getattr(instance, self.tokens[0]).upper()[0],
            getattr(instance, self.tokens[1]).upper()[0])
        return make_password(raw_password)


class LazyCompanyWebsiteReplacer(LazyReplacer):

    def apply(self, instance):
        return '{0}.example.com'.format(
            slugify(getattr(instance, self.tokens[0])))


class LazyCompanyEmailReplacer(LazyReplacer):
    TPL = '{0}.{1}@{2}.example.com'

    def apply(self, instance):
        return self.TPL.format(
            slugify(getattr(instance, self.tokens[0])),
            slugify(getattr(instance, self.tokens[1])),
            slugify(getattr(instance, self.tokens[2])))


class TextReplacer(LazyReplacer):
    tpl = None

    def __init__(self, tpl, tokens=None):
        self.tpl = tpl
        LazyReplacer.__init__(self, tokens)

    def apply(self, instance):
        vals = [getattr(instance, attr) for attr in self.tokens]
        return self.tpl.format(*vals)
