from django.core.exceptions import ImproperlyConfigured, ValidationError
from djfaker import replacers
from djfaker.exceptions import FakerUnicityError
from .helpers import FakerBaseTest
from .testapp.models import FakerTestA, FakerTestB
from .testapp.fakers import (FakerTestAFaker, FakerTestBFaker,
DummyInvalidFaker1, DummyInvalidFaker2, DummyInvalidFaker3,
DummyFakerWithoutDeletionQS, DummyFakerWithoutUpdateQS)


class ModelFakerTest(FakerBaseTest):
    """ Test ModelFaker class """

    def test__get_replacers(self):
        """ Test _get_replacers method """
        mf = FakerTestAFaker()
        self.assertEqual(['prop_w'], mf._get_replacers())
        self.assertEqual(['prop_x'], mf._get_replacers(replacers.SimpleReplacer))
        self.assertEqual(['prop_y'], mf._get_replacers(replacers.LazyReplacer))

    def test__validate(self):
        """ Test _validate method """
        mf = DummyInvalidFaker1()
        self.assertRaises(ImproperlyConfigured, mf._validate)
        mf = DummyInvalidFaker2()
        self.assertRaises(ImproperlyConfigured, mf._validate)
        mf = DummyInvalidFaker3()
        self.assertRaises(ImproperlyConfigured, mf._validate)

    def test__run_dependencies(self):
        """ Test _run_dependencies method """
        mf = FakerTestAFaker()
        mf._run_dependencies()
        self.assertTrue(FakerTestBFaker._ran)
        self.assertFalse(FakerTestAFaker._ran)

    def test__run_deletion(self):
        """ Test _run_deletion method """
        # Data set
        inst1 = FakerTestA(old=False)
        inst1.save()
        inst2 = FakerTestA(old=True)
        inst2.save()
        # Without QS_FOR_DELETION
        mf = DummyFakerWithoutDeletionQS()
        mf._run_deletion()
        qs = FakerTestA.objects.values_list('id', flat=True)
        self.assertEqual([inst1.pk, inst2.pk], list(qs))
        # With QS_FOR_DELETION which should delete instances marked 'old'
        mf = FakerTestAFaker()
        mf._run_deletion()
        qs = FakerTestA.objects.values_list('id', flat=True)
        self.assertEqual([inst1.pk], list(qs))

    def test__get_update_qs(self):
        """ Test _get_update_qs method """
        # Data set
        inst1 = FakerTestA(prop_w='foo')
        inst1.save()
        inst2 = FakerTestA(prop_w='bar')
        inst2.save()
        # Without QS_FOR_UPDATE
        mf = DummyFakerWithoutUpdateQS()
        qs = mf._get_update_qs().values_list('id', flat=True)
        self.assertEqual([inst1.pk, inst2.pk], list(qs))
        # With QS_FOR_UPDATE updating only instances with prop_w=='foo'
        mf = FakerTestAFaker()
        qs = mf._get_update_qs().values_list('id', flat=True)
        self.assertEqual([inst1.pk], list(qs))

    def test__run_update(self):
        """ Test _run_update method """
        # Data set
        inst1 = FakerTestA(prop_w='foo', prop_x='bar', prop_y='oxo')
        inst1.save()
        # Run update
        mf = FakerTestAFaker()
        mf._run_update()
        # Check result
        inst1 = FakerTestA.objects.get(pk=inst1.pk)
        self.assertEqual('dummyA', inst1.prop_w)
        self.assertEqual('Jack', inst1.prop_x)
        self.assertEqual('Hello Jack', inst1.prop_y)

    def test__run(self):
        """ Test all the whole process ! """
        # Data set
        instA1 = FakerTestA(prop_w='foo')   # Should be faked
        instA1.save()
        instA2 = FakerTestA(prop_w='fixed') # Should not be faked
        instA2.save()
        instA3 = FakerTestA(old=True)       # Should be deleted
        instA3.save()
        #---
        instB1 = FakerTestB()               # Should be faked by dependency
        instB1.save()
        # RUN !
        mf = FakerTestAFaker()
        mf._run()
        # Ensure fakers have been ran
        self.assertTrue(FakerTestBFaker._ran)
        self.assertTrue(FakerTestAFaker._ran)
        # Check instances states
        qs = FakerTestA.objects.values_list('id', flat=True)
        self.assertEqual(set([instA1.pk, instA2.pk]), set(qs))
        instA1 = FakerTestA.objects.get(pk=instA1.pk)
        self.assertEqual('dummyA', instA1.prop_w)
        instA2 = FakerTestA.objects.get(pk=instA2.pk)
        self.assertEqual('fixed', instA2.prop_w)
        instB1 = FakerTestB.objects.get(pk=instB1.pk)
        self.assertEqual('dummyB', instB1.prop_z)

    def test__run__no_deps(self):
        """ Test _run method with `no_deps` arg True """
        mf = FakerTestAFaker()
        mf._run(no_deps=True)
        self.assertFalse(FakerTestBFaker._ran)

    def test__run__no_dels(self):
        """ Test _run method with `no_dels` arg True """
        inst = FakerTestA(old=True)
        inst.save()
        mf = FakerTestAFaker()
        mf._run(no_dels=True)
        self.assertEqual(1, FakerTestA.objects.count())

    def test_broken_unicity(self):
        """ Test broken_unicity """
        def _mock_validate_unique(inst):
            _mock_msg = {'prop_unique': 'Imitated broken unicity constraint'}
            raise ValidationError(_mock_msg)
        setattr(FakerTestA, "validate_unique", _mock_validate_unique)
        inst = FakerTestA()
        inst.save()
        mf = FakerTestAFaker()
        self.assertRaises(FakerUnicityError, mf._run_update)

