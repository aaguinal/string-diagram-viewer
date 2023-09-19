import json
import os
import unittest
from json.decoder import JSONDecodeError

from sympy.categories import Object, CompositeMorphism

from categorytheory.Diagram import Diagram, StringDiagram
from categorytheory.MonoidalCategory import MonoidalObject, MonoidalMorphism, NamedMorphism, IdentityMorphism


class TestDiagram(unittest.TestCase):
    def setUp(self):
        self.A = MonoidalObject("1", "2")
        self.B = MonoidalObject("3", "4")
        self.C = MonoidalObject("3", "4", "5")
        self.D = MonoidalObject("6", "7")
        self.E = MonoidalObject("3", "4", "4")

        self.f = NamedMorphism(domain=self.A, codomain=self.B, name="f")
        self.g = NamedMorphism(domain=self.C, codomain=self.D, name="g")

    def test_asymm_diff(self):
        # base = {3, 4}, elements = {3, 4, 5} --> [5]
        diff = Diagram.asymm_diff(base=self.B.objects, elements=self.C.objects)
        self.assertEqual(diff, [Object("5")])

        # base = {3, 4}, elements = {3, 4, 4} --> [4]
        diff = Diagram.asymm_diff(base=self.B.objects, elements=self.E.objects)
        self.assertEqual(diff, [Object("4")])

        # base = {3, 4}, elements = {3, 4} --> []
        diff = Diagram.asymm_diff(base=self.B.objects, elements=self.B.objects)
        self.assertEqual(diff, [])

        # base = {3, 4, 5}, elements = {3, 4} --> []
        diff = Diagram.asymm_diff(base=self.C.objects, elements=self.B.objects)
        self.assertEqual(diff, [])

    def test_make_strings(self):
        self.assertEqual(Diagram.make_strings(self.A.objects), [IdentityMorphism(Object("1")),
                                                                IdentityMorphism(Object("2"))])
        self.assertEqual(Diagram.make_strings(self.A.objects + [self.B]), [IdentityMorphism(Object("1")),
                                                                           IdentityMorphism(Object("2")),
                                                                           IdentityMorphism(Object("3")),
                                                                           IdentityMorphism(Object("4"))])
        self.assertEqual(Diagram.make_strings([self.A, self.B]), [IdentityMorphism(Object("1")),
                                                                  IdentityMorphism(Object("2")),
                                                                  IdentityMorphism(Object("3")),
                                                                  IdentityMorphism(Object("4"))])

    def test_weave_pattern_1(self):
        # top:      [a b c d]   =>      [a b c d e]
        # bottom:   [a b e]     =>      [a b e c d]
        top_strings = Diagram.make_strings(objects=[MonoidalObject("a", "b", "c", "d")])
        bottom_strings = Diagram.make_strings(objects=[MonoidalObject("a", "b", "e")])
        Diagram.weave_pattern(cloth=top_strings, yarn=bottom_strings)
        Diagram.weave_pattern(cloth=bottom_strings, yarn=top_strings)

        true_top_strings = Diagram.make_strings(objects=[MonoidalObject("a", "b", "c", "d", "e")])
        self.assertEqual(top_strings, true_top_strings)
        true_bottom_strings = Diagram.make_strings(objects=[MonoidalObject("a", "b", "e", "c", "d")])
        self.assertEqual(bottom_strings, true_bottom_strings)

    def test_weave_pattern_2(self):
        # top:      [a b c d]       =>      [f a b c d]
        # bottom:   [f a b c d]     =>      [f a b c d]
        top_strings = Diagram.make_strings(objects=[MonoidalObject("a", "b", "c", "d")])
        bottom_strings = Diagram.make_strings(objects=[MonoidalObject("f", "a", "b", "c", "d")])
        Diagram.weave_pattern(cloth=top_strings, yarn=bottom_strings)
        Diagram.weave_pattern(cloth=bottom_strings, yarn=top_strings)

        true_top_strings = Diagram.make_strings(objects=[MonoidalObject("f", "a", "b", "c", "d")])
        self.assertEqual(top_strings, true_top_strings)
        true_bottom_strings = Diagram.make_strings(objects=[MonoidalObject("f", "a", "b", "c", "d")])
        self.assertEqual(bottom_strings, true_bottom_strings)

    def test_weave_pattern_3(self):
        # top:      [a b c d]       =>      [a b c d e]
        # bottom:   [a b e c]       =>      [a b e c d]
        top_strings = Diagram.make_strings(objects=[MonoidalObject("a", "b", "c", "d")])
        bottom_strings = Diagram.make_strings(objects=[MonoidalObject("a", "b", "e", "c")])
        Diagram.weave_pattern(cloth=top_strings, yarn=bottom_strings)
        Diagram.weave_pattern(cloth=bottom_strings, yarn=top_strings)

        true_top_strings = Diagram.make_strings(objects=[MonoidalObject("a", "b", "c", "d", "e")])
        self.assertEqual(top_strings, true_top_strings)
        true_bottom_strings = Diagram.make_strings(objects=[MonoidalObject("a", "b", "e", "c", "d")])
        self.assertEqual(bottom_strings, true_bottom_strings)

    def test_compute_swaps(self):
        a = MonoidalObject("a", "b", "c", "d", "e").objects
        b = MonoidalObject("a", "b", "e", "c", "d").objects
        swaps = Diagram.compute_swaps(a, b)
        self.assertEqual(swaps, [(Object("c"), Object("d")),
                                 (Object("d"), Object("c")),
                                 (Object("d"), Object("e")),
                                 (Object("c"), Object("e"))])

        b = MonoidalObject("a", "b", "e", "c").objects
        self.assertRaises(ValueError, Diagram.compute_swaps, a, b)

        b = MonoidalObject("a", "f", "e", "c", "d").objects
        self.assertRaises(ValueError, Diagram.compute_swaps, a, b)

    def test_add_braids(self):
        # Set-up
        f_morph = NamedMorphism(domain=MonoidalObject("foo"), codomain=MonoidalObject("a", "b", "c", "d", "e"), name="f")
        g_morph = NamedMorphism(domain=MonoidalObject("a", "b", "e", "c", "d"), codomain=MonoidalObject("bar"), name="g")
        f = Diagram(f_morph)
        g = Diagram(g_morph)
        fg_with_braids = Diagram.add_braids(f, g)

        # Test
        try:
            CompositeMorphism([d.morphism for d in fg_with_braids])
            success = True
        except ValueError:
            success = False
        self.assertTrue(success)

    def test_compose(self):
        f = Diagram(self.f)
        g = Diagram(self.g)
        h = f * g
        h_morphism = CompositeMorphism(h.morphisms)
        self.assertEqual(h_morphism.domain, h.domain)
        self.assertEqual(h_morphism.codomain, h.codomain)

    def test_compose_1(self):
        f_morph = NamedMorphism(domain=MonoidalObject("foo"), codomain=MonoidalObject("a", "b", "c", "d"), name="f")
        g_morph = NamedMorphism(domain=MonoidalObject("a", "b", "e"), codomain=MonoidalObject("bar"), name="g")

        f = Diagram(f_morph)
        g = Diagram(g_morph)
        h = f * g
        self.assertEqual(h.domain, MonoidalObject("foo", "e"))
        self.assertEqual(h.codomain, MonoidalObject("bar", "c", "d"))
        self.assertEqual(h.name, "f @ id_{e} "
                                 "* id_{a} @ id_{b} @ id_{c} @ τ(d, e) "
                                 "* id_{a} @ id_{b} @ τ(c, e) @ id_{d} "
                                 "* g @ id_{c} @ id_{d}")

    def test_compose_2(self):
        f_morph = NamedMorphism(domain=MonoidalObject("foo"), codomain=MonoidalObject("a", "b", "c", "d"), name="f")
        g_morph = NamedMorphism(domain=MonoidalObject("f", "a", "b", "c", "d"), codomain=MonoidalObject("bar"), name="g")

        f = Diagram(f_morph)
        g = Diagram(g_morph)
        h = f * g
        self.assertEqual(h.domain, MonoidalObject("f", "foo"))
        self.assertEqual(h.codomain, MonoidalObject("bar"))
        self.assertEqual(h.name, "id_{f} @ f * g")

    def test_compose_3(self):
        f_morph = NamedMorphism(domain=MonoidalObject("foo"), codomain=MonoidalObject("a", "b", "c", "d"), name="f")
        g_morph = NamedMorphism(domain=MonoidalObject("a", "b", "e", "c"), codomain=MonoidalObject("bar"), name="g")

        f = Diagram(f_morph)
        g = Diagram(g_morph)
        h = f * g
        self.assertEqual(h.domain, MonoidalObject("foo", "e"))
        self.assertEqual(h.codomain, MonoidalObject("bar", "d"))
        self.assertEqual(h.name, "f @ id_{e} "
                                 "* id_{a} @ id_{b} @ id_{c} @ τ(d, e) "
                                 "* id_{a} @ id_{b} @ τ(c, e) @ id_{d} "
                                 "* g @ id_{d}")

    def test_compose_4(self):
        f_morph = NamedMorphism(domain=MonoidalObject("foo"), codomain=MonoidalObject("a", "b", "c", "d"), name="f")
        g_morph = NamedMorphism(domain=MonoidalObject("x"), codomain=MonoidalObject("bar"), name="g")

        f = Diagram(f_morph)
        g = Diagram(g_morph)
        h = f * g
        self.assertEqual(h.domain, MonoidalObject("x", "foo"))
        self.assertEqual(h.codomain, MonoidalObject("bar", "a", "b", "c", "d"))
        self.assertEqual(h.name, "id_{x} @ f * g @ id_{a} @ id_{b} @ id_{c} @ id_{d}")

    def test_to_dict(self):
        f = Diagram(self.f)
        f_dict = dict(f)
        self.assertEqual(f_dict["name"], "f")
        self.assertEqual(f_dict["domain"], [Object("1"), Object("2")])
        self.assertEqual(f_dict["codomain"], [Object("3"), Object("4")])
        self.assertEqual(f_dict["linear_syntax"], "f: 1 @ 2 -> 3 @ 4")

    def test_to_json(self):
        f = Diagram(self.f)
        f_json = f.to_json()
        self.assertIsNotNone(json.loads(f_json))

    def test_slices(self):
        f = Diagram(self.f)
        f_slices = f.slices()
        self.assertEqual(len(f_slices), 3)

    def test_as_graph(self):
        f = Diagram(self.f)
        f_nodes, f_edges, f_size = f.as_graph()
        self.assertEqual(len(f_nodes), 5)
        self.assertEqual(len(f_edges), 4)
        self.assertEqual(f_size, (3, 2))

    def test_to_vis(self):
        f = Diagram(self.f)
        filename = os.path.join(os.path.dirname(__file__), "test_data.json")
        vis_data = f.to_vis(filename=filename)
        self.assertIsNotNone(json.dumps(vis_data))

    def tearDown(self) -> None:
        filenames = [os.path.join(os.path.dirname(__file__), "test_data.json")]
        for f in filenames:
            if os.path.exists(f):
                os.remove(f)


class TestStringDiagram(unittest.TestCase):
    def setUp(self) -> None:
        self.E = MonoidalObject("3", "4", "4")

        self.m1 = MonoidalMorphism(IdentityMorphism(domain=MonoidalObject("f")),
                                   NamedMorphism(name="f", domain=MonoidalObject("foo"),
                                                 codomain=MonoidalObject("a", "b", "c", "d")))
        self.m2 = NamedMorphism(name="g", domain=MonoidalObject("f", "a", "b", "c", "d"),
                                codomain=MonoidalObject("bar"))

        self.d1 = Diagram(self.m1)
        self.d2 = Diagram(self.m2)

    def test_init(self):
        sd = StringDiagram(diagrams=[self.d1, self.d2], name="MyStringDiagram")
        self.assertEqual(sd.name, "MyStringDiagram")
        self.assertEqual(sd._diagrams, (self.d1, self.d2))

    def test_init_err(self):
        A = MonoidalObject("1", "2")
        B = MonoidalObject("3", "4")

        C = MonoidalObject("3", "4", "5")
        D = MonoidalObject("6", "7")

        f = Diagram(NamedMorphism(domain=A, codomain=B, name="f"))
        g = Diagram(NamedMorphism(domain=C, codomain=D, name="g"))

        self.assertRaises(ValueError, StringDiagram, [f, g])

    def test_diagrams(self):
        sd = StringDiagram(diagrams=[self.d1, self.d2], name="MyStringDiagram")
        self.assertEqual(sd.diagrams, [self.d1, self.d2])

    def test_linear_syntax(self):
        sd = StringDiagram(diagrams=[self.d1, self.d2], name="MyStringDiagram")
        self.assertEqual(sd.linear_syntax, "id_{f} @ f * g")

    def test_morphisms(self):
        sd = StringDiagram(diagrams=[self.d1, self.d2], name="MyStringDiagram")
        self.assertEqual(sd.morphisms, [self.m1, self.m2])

    def test_domain(self):
        sd = StringDiagram(diagrams=[self.d1, self.d2], name="MyStringDiagram")
        self.assertEqual(sd.domain, MonoidalObject("f", "foo"))

    def test_codomain(self):
        sd = StringDiagram(diagrams=[self.d1, self.d2], name="MyStringDiagram")
        self.assertEqual(sd.codomain, MonoidalObject("bar"))

    def test_as_morphism(self):
        sd = StringDiagram(diagrams=[self.d1, self.d2], name="MyStringDiagram")
        self.assertEqual(sd.as_morphism(), CompositeMorphism(self.m1, self.m2))

    def test_len(self):
        sd = StringDiagram(diagrams=[self.d1, self.d2], name="MyStringDiagram")
        self.assertEqual(len(sd), 2)

    def test_str(self):
        sd = StringDiagram(diagrams=[self.d1, self.d2], name="MyStringDiagram")
        self.assertEqual(str(sd), "MyStringDiagram")

    def test_to_json(self):
        sd = StringDiagram(diagrams=[self.d1, self.d2], name="MyStringDiagram")
        sd_json = sd.to_json()
        try:
            loaded = json.loads(sd_json)
            self.assertIsNotNone(loaded)
            self.assertIsNotNone(loaded[1][0]["domain"])
            self.assertEqual(loaded[1][0]["domain"]["type"], "MonoidalObject")
        except (JSONDecodeError, TypeError):
            self.assertTrue(False)

    def test_to_slices(self):
        sd = StringDiagram(diagrams=[self.d1, self.d2], name="MyStringDiagram")
        sd_slices = sd.slices()
        self.assertEqual(len(sd_slices), 5)

    def test_compose_1(self):
        A = MonoidalObject("1", "2")
        B = MonoidalObject("3", "4")

        C = MonoidalObject("3", "4", "5")
        D = MonoidalObject("6", "7")

        E = MonoidalObject("6", "7", "8")
        F = MonoidalObject("bar")

        f = Diagram(NamedMorphism(domain=A, codomain=B, name="f"))
        g = Diagram(NamedMorphism(domain=C, codomain=D, name="g"))
        h = Diagram(NamedMorphism(domain=E, codomain=F, name="h"))

        # f: 1 @ 2 -> 3 @ 4
        # g: 3 @ 4 @ 5 -> 6 @ 7
        # h: 6 @ 7 @ 8 -> bar
        #
        # (f * g) * h =>
        # (f * g): 1 @ 2 @ 5 -> 6 @ 7
        # (f * g) * h: 1 @ 2 @ 5 @ 8 -> bar

        k = (f * g) * h
        self.assertEqual(k.domain, MonoidalObject("1", "2", "5", "8"))
        self.assertEqual(k.codomain, MonoidalObject("bar"))
        self.assertEqual(k.linear_syntax, "f @ id_{5} @ id_{8} * g @ id_{8} * h")

    def test_compose_2(self):
        A = MonoidalObject("1", "2")
        B = MonoidalObject("3", "4", "foo")

        C = MonoidalObject("3", "4", "5")
        D = MonoidalObject("6", "7")

        E = MonoidalObject("6", "7", "8")
        F = MonoidalObject("bar")

        f = Diagram(NamedMorphism(domain=A, codomain=B, name="f"))
        g = Diagram(NamedMorphism(domain=C, codomain=D, name="g"))
        h = Diagram(NamedMorphism(domain=E, codomain=F, name="h"))

        # f: 1 @ 2 -> 3 @ 4 @ foo
        # g: 3 @ 4 @ 5 -> 6 @ 7
        # h: 6 @ 7 @ 8 -> bar
        #
        # (f * g) * h =>
        # (f * g): 1 @ 2 @ 5 -> 6 @ 7 @ foo
        # (f * g) * h: 1 @ 2 @ 5 @ 8 -> bar @ foo

        k = (f * g) * h
        self.assertEqual(k.domain, MonoidalObject("1", "2", "5", "8"))
        self.assertEqual(k.codomain, MonoidalObject("bar", "foo"))

    def test_compose_3(self):
        A = MonoidalObject("1", "2")
        B = MonoidalObject("3", "4", "foo")

        C = MonoidalObject("3", "4", "5")
        D = MonoidalObject("6", "7")

        E = MonoidalObject("6", "7", "8")
        F = MonoidalObject("bar")

        G = MonoidalObject("bar", "foo")
        H = MonoidalObject("9")

        f = Diagram(NamedMorphism(domain=A, codomain=B, name="f"))
        g = Diagram(NamedMorphism(domain=C, codomain=D, name="g"))
        h = Diagram(NamedMorphism(domain=E, codomain=F, name="h"))
        i = Diagram(NamedMorphism(domain=G, codomain=H, name="i"))

        # f: 1 @ 2 -> 3 @ 4 @ foo
        # g: 3 @ 4 @ 5 -> 6 @ 7
        # h: 6 @ 7 @ 8 -> bar
        # i: bar @ foo -> 9
        #
        # (f * g) * (h * i) =>
        # (f * g): 1 @ 2 @ 5 -> 6 @ 7 @ foo
        # (h * i): 6 @ 7 @ 8 @ foo -> 9
        # (f * g) * (h * i): 1 @ 2 @ 5 @ 8 -> 9

        k = (f * g) * (h * i)
        self.assertEqual(k.domain, MonoidalObject("1", "2", "5", "8"))
        self.assertEqual(k.codomain, MonoidalObject("9"))

    def test_as_graph(self):
        sd = StringDiagram(diagrams=[self.d1, self.d2], name="MyStringDiagram")
        sd_nodes, sd_edges, sd_size = sd.as_graph()
        self.assertEqual(len(sd_nodes), 11)
        self.assertEqual(len(sd_edges), 13)
        self.assertEqual(sd_size, (5, 5))

    def test_as_vis(self):
        sd = StringDiagram(diagrams=[self.d1, self.d2], name="MyStringDiagram")
        filename = os.path.join(os.path.dirname(__file__), "test_data.json")
        sd_vis_data = sd.to_vis(filename=filename)
        self.assertIsNotNone(json.dumps(sd_vis_data))

    def tearDown(self) -> None:
        filenames = [os.path.join(os.path.dirname(__file__), "test_data.json")]
        for f in filenames:
            if os.path.exists(f):
                os.remove(f)


if __name__ == "__main__":
    unittest.main()
