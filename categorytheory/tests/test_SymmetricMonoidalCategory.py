import unittest

from sympy import FiniteSet
from sympy.categories import Object, Diagram, CompositeMorphism

from categorytheory.MonoidalCategory import MonoidalObject, MonoidalCategory, MonoidalMorphism, NamedMorphism, IdentityMorphism
from categorytheory.SymmetricMonoidalCategory import SymmetricMonoidalCategory


class TestSymmetricMonoidalCategory(unittest.TestCase):
    def setUp(self) -> None:
        self.A = MonoidalObject("1", "2")
        self.B = MonoidalObject("3", "4")
        self.C = MonoidalObject("5", "6")

        self.f = NamedMorphism(domain=self.A, codomain=self.B, name="f")
        self.g = NamedMorphism(domain=self.B, codomain=self.C, name="g")

        self.f_monoidal = MonoidalMorphism(self.f)
        self.g_monoidal = MonoidalMorphism(self.g)

    def test_init(self):
        objects = [self.A, self.B, self.C]
        d = Diagram([self.f, self.g])
        C = MonoidalCategory(name="C", objects=objects, commutative_diagrams=[d])

        self.assertEqual(C.name, "C")
        self.assertEqual(C.objects.args[0], objects)
        self.assertEqual(C.commutative_diagrams, FiniteSet(d))

    def test_swap(self):
        x = Object("hi")
        y = Object("bye")
        t = SymmetricMonoidalCategory.swap(x, y)

        self.assertEqual(t.domain, MonoidalObject(x, y))
        self.assertEqual(t.codomain, MonoidalObject(y, x))

    def test_check_braid_identity(self):
        x = Object("hi")
        y = Object("bye")
        z = Object("hello")

        t1 = SymmetricMonoidalCategory.swap(x, y)
        t2 = SymmetricMonoidalCategory.swap(y, x)
        self.assertTrue(SymmetricMonoidalCategory._check_braid_identity_(t1, t2))

        t1 = SymmetricMonoidalCategory.swap(x, y)
        t2 = SymmetricMonoidalCategory.swap(y, z)
        self.assertFalse(SymmetricMonoidalCategory._check_braid_identity_(t1, t2))

        t1 = SymmetricMonoidalCategory.swap(x, y)
        t2 = SymmetricMonoidalCategory.swap(z, x)
        self.assertFalse(SymmetricMonoidalCategory._check_braid_identity_(t1, t2))

        t1 = MonoidalMorphism(NamedMorphism(domain=MonoidalObject("foo"), codomain=MonoidalObject(y, x), name="t1"))
        t2 = MonoidalMorphism(NamedMorphism(domain=MonoidalObject(y, x), codomain=MonoidalObject("foo"), name="t2"))
        self.assertFalse(SymmetricMonoidalCategory._check_braid_identity_(t1, t2))  # should fail bc they're not swaps

    def test_apply_braid_identity(self):
        x = Object("hi")
        y = Object("bye")
        z = Object("hello")

        t1 = SymmetricMonoidalCategory.swap(x, y)
        t2 = SymmetricMonoidalCategory.swap(y, x)
        self.assertEqual(SymmetricMonoidalCategory.apply_braid_identity(t1, t2), IdentityMorphism(MonoidalObject(x, y)))

        t2 = MonoidalMorphism(NamedMorphism(domain=MonoidalObject(y, x), codomain=MonoidalObject("foo"), name="t2"))
        self.assertEqual(SymmetricMonoidalCategory.apply_braid_identity(t1, t2), CompositeMorphism(t1, t2))

        t2 = MonoidalMorphism(NamedMorphism(domain=MonoidalObject(z, x), codomain=MonoidalObject("foo"), name="t2"))
        self.assertRaises(ValueError, SymmetricMonoidalCategory.apply_braid_identity, t1, t2)

    def test_simplify(self):
        # Set-up
        x = Object("hi")
        y = Object("bye")
        z = Object("hello")

        t1 = SymmetricMonoidalCategory.swap(x, y)
        t2 = SymmetricMonoidalCategory.swap(y, x)
        t3 = SymmetricMonoidalCategory.swap(x, z)
        t4 = SymmetricMonoidalCategory.swap(z, y)

        # Tests
        new_swaps = SymmetricMonoidalCategory.simplify([t1, t2, t3, t4])
        self.assertEqual(new_swaps, [t3, t4])

        t4 = SymmetricMonoidalCategory.swap(x, y)
        new_swaps = SymmetricMonoidalCategory.simplify([t1, t2, t3, t4])
        self.assertEqual(new_swaps, [t3, t4])

        new_swaps = SymmetricMonoidalCategory.simplify([t1])
        self.assertEqual(new_swaps, [t1])
        pass


if __name__ == '__main__':
    unittest.main()
