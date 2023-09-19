from sympy.categories import Object, Morphism, CompositeMorphism

from categorytheory.MonoidalCategory import MonoidalCategory, MonoidalObject, MonoidalMorphism, NamedMorphism, IdentityMorphism


class SymmetricMonoidalCategory(MonoidalCategory):
    def __new__(cls, name, objects, commutative_diagrams):
        return MonoidalCategory.__new__(cls, name, objects, commutative_diagrams)

    @staticmethod
    def swap(x: Object, y: Object) -> MonoidalMorphism:
        A = MonoidalObject(x, y)
        B = MonoidalObject(y, x)
        name = "\u03C4({x.name}, {y.name})".format(x=x, y=y)  # \u03C4 = Greek small letter tau
        return MonoidalMorphism(NamedMorphism(domain=A, codomain=B, name=name), is_swap=True)

    @staticmethod
    def _check_braid_identity_(t1: MonoidalMorphism, t2: MonoidalMorphism):
        if not (t1.is_swap and t2.is_swap):  # both must be swaps
            return False

        try:
            composed = CompositeMorphism(t1, t2)
        except ValueError:
            return False

        if composed.domain == composed.codomain:
            return True
        return False

    @staticmethod
    def apply_braid_identity(t1: MonoidalMorphism, t2: MonoidalMorphism) -> Morphism:
        if SymmetricMonoidalCategory._check_braid_identity_(t1, t2):
            return IdentityMorphism(domain=t1.domain)
        else:
            try:
                composite = CompositeMorphism(t1, t2)
                return composite  # hmmm... should it return composite or list of original morphisms?
            except ValueError:
                raise ValueError("Cannot compose morphisms and does not satisfy braid identity!")

    @staticmethod
    def simplify(swaps: list) -> list:
        # Start:    A B C D E
        # End:      A B E C D
        # In cycle notation, swaps = [(C D), (D C), (D E), (C E)]
        # simplify(swaps) = [(D E), (C E)]

        if len(swaps) < 2:
            # nothing to check, need at least two swaps to check braid identity
            return swaps

        new_swaps = []
        swap_1 = swaps.pop(0)
        while swaps:  # while there are still swaps that haven't been popped
            swap_2 = swaps.pop(0)
            if SymmetricMonoidalCategory._check_braid_identity_(swap_1, swap_2):
                swap_1 = swaps.pop(0)  # if they make identity, move on to next swap
            else:
                new_swaps.append(swap_1)
                swap_1 = swap_2
        new_swaps.append(swap_1)
        return new_swaps
