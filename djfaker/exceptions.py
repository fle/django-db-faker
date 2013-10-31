""" Custom exceptions """
from django.utils.translation import ugettext as ug
from django.db import IntegrityError

class FakerUnicityError(Exception):
    """ Exception raised if faker could not satisfy unicity contraints """

    def __init__(self, fields):
        self.fields = fields

    def __str__(self):
        msg = '{0} : {1}'.format(
            ug("Can't find a unique value for field(s)"),
            ', '.join(self.fields)
        )
        return msg
