""" Test custom exceptions """
from djfaker.exceptions import FakerUnicityError
from .helpers import FakerBaseTest

class FakerUnicityErrorTest(FakerBaseTest):
    """ Test FakerUnicityError class """

    def test___str__(self):
        """ Test __str__ method """
        try:
            raise FakerUnicityError(('field1', 'field2'))
        except FakerUnicityError, e:
            msg = "Can't find a unique value for field(s) : field1, field2"
            self.assertEqual(msg, str(e))
