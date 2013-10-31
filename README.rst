A module to help you faking a full django `Django <https://www.djangoproject.com>`_ application database.

It provides:

* A base class `ModelFaker` that you can implement and associate to your Django Model to describe how to fake it
* Basic replacers (you can easily extend), to replace database data by simple or built fake data
* A dependency management to play fakers in the order you need
* Signals, to do things you need before or after model faking

.. image:: https://travis-ci.org/fle/django-db-faker.png?branch=master
        :target: https://travis-ci.org/fle/django-db-faker

.. image:: https://coveralls.io/repos/fle/django-db-faker/badge.png
       :target: https://coveralls.io/r/fle/django-db-faker
