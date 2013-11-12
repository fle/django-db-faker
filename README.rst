A module to help you faking a full django `Django <https://www.djangoproject.com>`_ application database.

It provides:

* A base class `ModelFaker` that you can implement and associate to a Django Model to describe how to fake it
* Basic replacers (you can easily extend), to replace database data by simple or built fake data
* A dependency management to play fakers in the order you need
* Signals, to do things you need before or after model faking

.. image:: https://travis-ci.org/fle/django-db-faker.png?branch=master
        :target: https://travis-ci.org/fle/django-db-faker

.. image:: https://coveralls.io/repos/fle/django-db-faker/badge.png
       :target: https://coveralls.io/r/fle/django-db-faker


INSTALL
==================

Install:

::

    pip install https://github.com/fle/django-db-faker/archive/0.1.tar.gz


Add ``djfaker`` to your ``INSTALLED_APPS``:

::

    # settings.py
    INSTALLED_APPS = (
    ...
    'djfaker',
    )


USAGE
==================

Example
-----------
Here is an example of a basic app ``app_bank``:
* A ``Person`` owns an ``Account``, idenfified by a ``numero``
* An ``Account`` marked as ``closed`` is quite obsolete

::

    #models.py

    class Person(models.Model):
        lastname = models.CharField(max_length=100)
        city = models.CharField(max_length=100)

    class Account(models.Model):
        person = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='accounts')
        numero = models.IntegerField(unique=True)
        closed = BooleanField(default=False)

We want to anonymize (change confidential data) and simplify this database while keeping a consistent structure:
* Change Person.lastname
* Change Account.numero
* Remove Persons without account
* Remove Accounts marked as ``closed``


Write basic fakers
-------------------
Add a fakers.py in you app to replace basic properties

::

    # fakers.py

    from djfaker import replacers

    class PersonFaker(ModelFaker):
        FAKER_FOR = models.Person
        lastname = replacers.ChoiceReplacer(choices=['Adams', 'Doe', 'Clayton', ...])
        
    class AccountFaker(ModelFaker):
        FAKER_FOR = models.Person
        numero = replacers.SerialReplacer()


Manage deletions
----------------
Use ``QS_FOR_DELETION`` to delete accounts marked as ``closed`` and persons without account:

::

    class PersonFaker(ModelFaker):
        FAKER_FOR = models.Person
        QS_FOR_DELETION = lambda x: Person.objects.filter(accounts__isnull=True)
        numero = replacers.SerialReplacer()

    class AccountFaker(ModelFaker):
        FAKER_FOR = models.Person
        QS_FOR_DELETION = lambda x: Account.objects.filter(closed=True)
        numero = replacers.SerialReplacer()


Manage dependencies
-------------------
Use ``DEPENDS_ON`` to delete closed accounts before deleting persons without account:

::

    class PersonFaker(ModelFaker):
        FAKER_FOR = models.Person
        QS_FOR_DELETION = lambda x: Person.objects.filter(accounts__isnull=True)
        DEPENDS_ON = ('app_bank.fakers.AccountFaker', )
        numero = replacers.SerialReplacer()

    class AccountFaker(ModelFaker):
        FAKER_FOR = models.Person
        QS_FOR_DELETION = lambda x: Account.objects.filter(closed=True)
        numero = replacers.SerialReplacer()


Fake it !
---------
Run provided command to fake this app:

::

    # Simple usage
    ./manage.py faker_fake_db

A few options are available here

::

    # Fake only a given app
    ./manage.py faker_fake_db app_bank

    # Fake only a given model
    ./manage.py faker_fake_db app_bank.PersonFaker

    # Fake only a given model and do not take care of dependencies
    ./manage.py faker_fake_db app_bank.PersonFaker --no-deps

    # Fake only a given model and do not run deletions
    ./manage.py faker_fake_db app_bank.AccountFaker --no-deps --no-dels


SETTINGS
==================
When data faking break a unicity constraint, script retry (quite stupidly) to fake instance.
A setting is available allows to limit number of tries

::

    DJFAKER_MAX_TRIES = 2  # default 3

REPLACING DATA
==================

Basic replacing
---------------
You can simply give a builtin type (int, boolean, string, ...)
value which will be set for each instance

::

    class PersonFaker(ModelFaker):
        city = "Nantes"

djfaker replacers
---------------
djfaker provides 2 types of replacer:
* Simple replacers: which are not dependent of the instance other fields (played first).
They just inherit from ``SimpleReplacer`` implement a method ``apply``.
Example:

::

    class SimpleReplacer(BaseReplacer):
        def apply(self):
            raise NotImplementedError


    class ChoiceReplacer(SimpleReplacer):
        choices = []

        def __init__(self, choices=None):
            if choices:
                self.choices = choices

        def apply(self):
            return choice(self.choices)




* Lazy replacers: which are dependent of the instance other fields (played last).
They inherit from ``LazyReplacer`` implement a method ``apply``. ``tokens`` must be attributes names of model you wan to fake.
Method ``apply`` take instance as an argument.
Example:
``tokens`` must be attribute names of Example:

::

    class LazyReplacer(BaseReplacer):
        tokens = []

        def __init__(self, tokens=None):
            if tokens:
                self.tokens = tokens

        def apply(self, instance):
            raise NotImplementedError


    class LazyUsernameReplacer(LazyReplacer):
        tokens = []

        def __init__(self, tokens=None):
            if tokens:
                self.tokens = tokens

        def apply(self, instance):
            return '{0}.{1}'.format(
                slugify(getattr(instance, self.tokens[0])),
                slugify(getattr(instance, self.tokens[1])))

You can easily extend them both and create your own replacer in few lines.

WARNING
==================
Don't do this in production :) !

You can adapt you settings to add ``djfaker`` to your ``INSTALLED_APPS`` only
on a development or test instance for more security.

::

    # settings.py

    USE_DJFAKER = False

    INSTALLED_APPS = (
    ...
    )

    try:
        from localsettings import *
    except ImportError:
        pass

    if USE_DJFAKER:
        INSTALLED_APPS += ('djfaker', )

::

    # localsettings.py

    USE_DJFAKER = True
