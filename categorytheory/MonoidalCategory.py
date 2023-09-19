from sympy import Basic, Symbol
from sympy.categories import Object, Category, Morphism, IdentityMorphism, NamedMorphism


class MonoidalObject:
    # https://github.com/oxford-quantum-group/discopy/blob/main/discopy/monoidal.py
    def __init__(self, *objects):
        self._objects = tuple(
            x if isinstance(x, Object) or x == [] else Object(x) for x in objects)

    @property
    def objects(self):
        return list(self._objects)

    @property
    def name(self):
        return " @ ".join([o.name for o in self.objects])

    def asdict(self):
        return dict(name=self.name,
                    objects=[o.name for o in self.objects],
                    type="MonoidalObject")

    def is_Symbol(self):
        # Added to handle sympy upgrades to new objects
        # https://docs.sympy.org/latest/modules/core.html?highlight=symbol#id26
        # FIXME: need to handle symbols as objects
        return False

    def __str__(self):
        return self.name

    def __len__(self):
        return len(self.objects)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __getitem__(self, key):
        if isinstance(key, slice):
            return MonoidalObject(*self.objects[key])
        return self.objects[key]

    def tensor(self, *others):
        for other in others:
            if not isinstance(other, MonoidalObject):
                raise TypeError("Can only tensor MonoidalObject!")
        # Add all objects within Monoidal Objects
        return MonoidalObject(*sum([m.objects for m in [self] + list(others)], []))

    def count(self, ob):
        ob, = ob if isinstance(ob, MonoidalObject) else (ob,)
        return self.objects.count(ob)

    def __matmul__(self, other):
        return self.tensor(other)

    def __add__(self, other):
        return self.tensor(other)

    def __eq__(self, other):
        if not isinstance(other, MonoidalObject):
            raise TypeError("Can only check equality for MonoidalObject!")
        return self.objects == other.objects

    def __hash__(self):
        return hash(self.name)

    def __sympy__(self):
        return self


class NamedMorphism(NamedMorphism):
    def __new__(cls, domain, codomain, name):
        if not name:
            raise ValueError("Empty morphism names not allowed.")

        if not isinstance(name, Symbol):
            name = Symbol(name)

        return Basic.__new__(cls, domain, codomain, name)

    def __iter__(self):
        yield "domain", self.domain.asdict()
        yield "codomain", self.codomain.asdict()
        yield "name", self.name
        yield "type", "NamedMorphism"

    def inverse(self):
        return NamedMorphism(name=self.name, domain=self.codomain, codomain=self.domain)


class IdentityMorphism(IdentityMorphism):
    def __new__(cls, domain):
        if isinstance(domain, Object):
            return Basic.__new__(cls, MonoidalObject(domain))  # make all objects MonoidalObjects
        return Basic.__new__(cls, domain)

    @property
    def name(self):
        return "id_{{{}}}".format(self.domain.name)

    def __eq__(self, other):
        if isinstance(other, IdentityMorphism):
            return self.name == other.name
        return NotImplementedError

    def __iter__(self):
        yield "domain", self.domain.asdict()
        yield "codomain", self.codomain.asdict()
        yield "name", self.name
        yield "type", "IdentityMorphism"

    def inverse(self):
        return self


class MonoidalMorphism(Morphism):
    def __new__(cls, *morphisms, is_swap: bool = False):
        return Basic.__new__(cls, *morphisms)

    def __init__(self, *morphisms, is_swap: bool = False):
        m = []
        for x in morphisms:
            if isinstance(x, (IdentityMorphism, NamedMorphism)):
                m.append(x)
            elif isinstance(x, MonoidalMorphism):
                m = m + x.morphisms
        self._morphisms = tuple(m)
        self._is_swap = is_swap

    @property
    def morphisms(self):
        return list(self._morphisms)

    @property
    def name(self):
        return " @ ".join([m.name for m in self.morphisms])

    @property
    def domain(self):
        return MonoidalObject(*sum([m.domain.objects for m in self.morphisms], []))

    @property
    def codomain(self):
        return MonoidalObject(*sum([m.codomain.objects for m in self.morphisms], []))

    @property
    def is_swap(self):
        # added flag to signal that this morphism is just swapping strings..
        # not sure if this makes the most sense here
        return self._is_swap

    def inverse(self):
        return MonoidalMorphism(*[m.inverse() for m in self.morphisms])

    def tensor(self, *others):
        valid_others = []
        for other in others:
            if not isinstance(other, Morphism):
                raise TypeError("Can only tensor Morphisms!")
            if not isinstance(other, MonoidalMorphism):
                valid_others.append(MonoidalMorphism(other))
            else:
                valid_others.append(other)
        return MonoidalMorphism(
            *sum([m.morphisms for m in [self] + list(valid_others)], [])
        )

    def slice(self):
        domain_id = [IdentityMorphism(o) for o in self.domain.objects]
        morphisms = self.morphisms
        codomain_id = [IdentityMorphism(o) for o in self.codomain.objects]
        return [domain_id, morphisms, codomain_id]

    def __str__(self):
        return self.name

    def __add__(self, other):
        return self.tensor(other)

    def __eq__(self, other):
        if isinstance(other, MonoidalMorphism):
            return self.name == other.name
        return NotImplemented

    def __hash__(self):
        return hash(self.name)

    def asdict(self):
        return [dict(m) for m in self.morphisms]

    def __sympy__(self):
        return self


class MonoidalCategory(Category):
    def __new__(cls, name, objects, commutative_diagrams):
        return Category.__new__(cls, name, objects, commutative_diagrams)

    def hom(self, src: MonoidalObject, tar: MonoidalObject):
        return [d.hom(src, tar)[0] for d in self.commutative_diagrams.args]

    @property
    def morphisms(self):
        morphisms = []
        for d in self.commutative_diagrams.args:
            morphisms = morphisms + [m for m, _ in d.premises.args]
        return morphisms

    @staticmethod
    def json_encoder(o):
        if isinstance(o, Object):
            return o.name
        if isinstance(o, Morphism):
            return dict(o)
