import unittest

from sympy import FiniteSet
from sympy.categories import Object, CompositeMorphism, Diagram

from categorytheory.MonoidalCategory import MonoidalObject, MonoidalMorphism, MonoidalCategory, NamedMorphism, IdentityMorphism


class TestMonoidalObject(unittest.TestCase):
    def test_instance_single_str(self):
        foo = MonoidalObject("a")
        self.assertEqual(foo.objects, [Object("a")])

    def test_instance_multi_str(self):
        foo = MonoidalObject("a", "b")
        self.assertEqual(foo.objects, [Object("a"), Object("b")])

    def test_instance_multi_object(self):
        foo = MonoidalObject(Object("a"), Object("b"))
        self.assertEqual(foo.objects, [Object("a"), Object("b")])

    def test_name_attr(self):
        foo = MonoidalObject("a", "b")
        self.assertEqual(foo.name, "a @ b")

    def test_tensor(self):
        foo = MonoidalObject("a", "b")
        bar = MonoidalObject("c", "d")
        foo = foo.tensor(bar)
        self.assertEqual(foo.name, "a @ b @ c @ d")
        self.assertEqual(foo.objects, [Object("a"), Object("b"), Object("c"), Object("d")])

    def test_tensor_multi(self):
        foo = MonoidalObject("a", "b")
        bar1 = MonoidalObject("c", "d")
        bar2 = MonoidalObject("e", "f")
        foo = foo.tensor(bar1, bar2)
        self.assertEqual(foo.name, "a @ b @ c @ d @ e @ f")
        self.assertEqual(foo.objects, [Object("a"), Object("b"), Object("c"), Object("d"), Object("e"), Object("f")])

    def test_add(self):
        foo = MonoidalObject("a", "b")
        bar = MonoidalObject("c", "d")
        foo = foo + bar
        self.assertEqual(foo.name, "a @ b @ c @ d")
        self.assertEqual(foo.objects, [Object("a"), Object("b"), Object("c"), Object("d")])

    def test_count(self):
        foo = MonoidalObject("a", "b", "a")
        count = foo.count(Object("a"))
        self.assertEqual(count, 2)

    def test_len(self):
        foo = MonoidalObject("a", "b", "a")
        self.assertEqual(len(foo), 3)

    def test_get_item(self):
        foo = MonoidalObject("a", "b")
        self.assertEqual(foo[0], Object("a"))
        self.assertEqual(foo[1], Object("b"))

    def test_iter(self):
        foo = MonoidalObject("a", "b")
        try:
            iter(foo)
        except TypeError:
            self.assertTrue(False)
        self.assertTrue(True)

    def test_identity_morphism(self):
        foo = MonoidalObject("a", "b")
        id_foo = IdentityMorphism(foo)
        self.assertEqual(id_foo.domain, foo)
        self.assertEqual(id_foo.codomain, foo)
        self.assertEqual(id_foo.name, "id_{a @ b}")
        pass

    def test_compose_morphism_monoidal(self):
        A = MonoidalObject("1", "2")
        B = MonoidalObject("3", "4")
        C = MonoidalObject("5", "6")

        f = NamedMorphism(domain=A, codomain=B, name="f")
        g = NamedMorphism(domain=B, codomain=C, name="g")

        h = CompositeMorphism(f, g)
        self.assertEqual(h, g * f)


class TestMonoidalMorphism(unittest.TestCase):
    def setUp(self) -> None:
        self.A = MonoidalObject("1", "2")
        self.B = MonoidalObject("3", "4")
        self.C = MonoidalObject("5", "6")

        self.id_A = IdentityMorphism(self.A)

        self.f = NamedMorphism(domain=self.A, codomain=self.B, name="f")
        self.g = NamedMorphism(domain=self.B, codomain=self.C, name="g")

        self.f_monoidal = MonoidalMorphism(self.f)
        self.g_monoidal = MonoidalMorphism(self.g)

        self.m = MonoidalMorphism(self.f, self.g)
        self.m_and_id = MonoidalMorphism(self.f, self.id_A)

    def test_init_1(self):
        self.assertEqual(self.m._morphisms, (self.f, self.g))
        self.assertEqual(self.m.domain, self.A + self.B)
        self.assertEqual(self.m.codomain, self.B + self.C)

    def test_init_2(self):
        h = "foo"
        m = MonoidalMorphism(self.f, self.g, h)
        self.assertEqual(m._morphisms, (self.f, self.g))
        self.assertEqual(m.domain, self.A + self.B)
        self.assertEqual(m.codomain, self.B + self.C)

    def test_init_3(self):
        m = MonoidalMorphism(self.f, self.g, self.m)
        self.assertEqual(m._morphisms, (self.f, self.g, self.f, self.g))
        self.assertEqual(m.domain, self.A + self.B + self.A + self.B)
        self.assertEqual(m.codomain, self.B + self.C + self.B + self.C)

    def test_init_4(self):
        self.assertEqual(self.m_and_id._morphisms, (self.f, self.id_A))
        self.assertEqual(self.m_and_id.domain, self.A + self.A)
        self.assertEqual(self.m_and_id.codomain, self.B + self.A)

    def test_morphisms_prop(self):
        self.assertEqual(self.m.morphisms, [self.f, self.g])

    def test_name_prop(self):
        self.assertEqual(self.m.name, "f @ g")

    def test_domain_prop(self):
        self.assertEqual(self.m.domain, MonoidalObject("1", "2", "3", "4"))
        self.assertEqual(self.m_and_id.domain, MonoidalObject("1", "2", "1", "2"))

    def test_codomain_prop(self):
        self.assertEqual(self.m.codomain, MonoidalObject("3", "4", "5", "6"))
        self.assertEqual(self.m_and_id.codomain, MonoidalObject("3", "4", "1", "2"))

    def test_slice(self):
        # f @ g: (1 @ 2 @ 3 @ 4) --> (3 @ 4 @ 5 @ 6)
        # => [[id(1), id(2), id(3), id(4)], [f, g], [id(3), id(4), id(5), id(6)]

        m_slices = self.m.slice()
        self.assertEqual(m_slices[0], [IdentityMorphism(Object("1")),
                                       IdentityMorphism(Object("2")),
                                       IdentityMorphism(Object("3")),
                                       IdentityMorphism(Object("4"))])
        self.assertEqual(m_slices[1], [self.f, self.g])
        self.assertEqual(m_slices[2], [IdentityMorphism(Object("3")),
                                       IdentityMorphism(Object("4")),
                                       IdentityMorphism(Object("5")),
                                       IdentityMorphism(Object("6"))])

    def test_tensor(self):
        m_prime = self.m + self.m
        self.assertEqual(m_prime.name, "f @ g @ f @ g")
        self.assertEqual(m_prime.domain.name, "1 @ 2 @ 3 @ 4 @ 1 @ 2 @ 3 @ 4")
        self.assertEqual(m_prime.codomain.name, "3 @ 4 @ 5 @ 6 @ 3 @ 4 @ 5 @ 6")

    def test_compose(self):
        m_prime = self.g_monoidal * self.f_monoidal
        self.assertEqual(m_prime.domain.name, "1 @ 2")
        self.assertEqual(m_prime.codomain.name, "5 @ 6")
        self.assertEqual(m_prime.components, (self.f_monoidal, self.g_monoidal))


class TestMonoidalCategory(unittest.TestCase):
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

    def test_hom(self):
        objects = [self.A, self.B, self.C]
        d = Diagram([self.f, self.g])
        C = MonoidalCategory(name="C", objects=objects, commutative_diagrams=[d])

        homset_A_C = C.hom(self.A, self.C)
        self.assertEqual(len(homset_A_C), 1)

        homset_A_B = C.hom(self.A, self.B)
        self.assertEqual(len(homset_A_B), 1)

    def test_morphisms(self):
        objects = [self.A, self.B, self.C]
        d = Diagram([self.f, self.g])
        C = MonoidalCategory(name="C", objects=objects, commutative_diagrams=[d])

        morphisms = C.morphisms

        self.assertIn(self.f, morphisms)
        self.assertIn(self.g, morphisms)

        self.assertIn(self.g * self.f, morphisms)

        self.assertIn(IdentityMorphism(self.A), morphisms)
        self.assertIn(IdentityMorphism(self.B), morphisms)
        self.assertIn(IdentityMorphism(self.C), morphisms)


if __name__ == '__main__':
    unittest.main()
