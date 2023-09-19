import collections
import json
from typing import List

import numpy as np
from sympy.categories import Object, CompositeMorphism, Morphism

from categorytheory.MonoidalCategory import MonoidalMorphism, NamedMorphism, IdentityMorphism, MonoidalObject, \
    MonoidalCategory
from categorytheory.SymmetricMonoidalCategory import SymmetricMonoidalCategory


class Diagram:
    def __init__(self, morphism: NamedMorphism or MonoidalMorphism or IdentityMorphism, name: str or None = None):
        self.morphism = morphism
        self.domain = self.morphism.domain
        self.codomain = self.morphism.codomain
        if name is None:
            self.name = self.morphism.name
        else:
            self.name = name

    @property
    def linear_syntax(self):
        return "{morphism_name}: {domain} -> {codomain}".format(morphism_name=self.name, domain=self.domain,
                                                                codomain=self.codomain)

    def as_morphism(self):
        return MonoidalMorphism(self.morphism)

    @staticmethod
    def _find_morphism_with_string(morphisms: list, morphisms_rank: int, string: IdentityMorphism, mapped_nodes: list,
                                   use_domain: bool = False) -> (Morphism, int) or (None, None):
        for col, m in enumerate(morphisms):
            node_id = "{}_({})_({})".format(m.name, morphisms_rank, col)
            if use_domain:
                compare_strings = Diagram.make_strings(m.domain.objects)
            else:
                compare_strings = Diagram.make_strings(m.codomain.objects)
            if string in compare_strings:
                string_index = 0
                if type(m) == NamedMorphism:
                    # handle when morphism has a codomain string that is the same as another morphism in that slice
                    ind = [i for i, s in enumerate(compare_strings) if string == s]
                    for i in ind:
                        node_id_with_index = "{}_({})".format(node_id, i)  # note index of codomain string that matched
                        if node_id_with_index not in mapped_nodes:
                            string_index = i
                            return node_id, string_index
                else:
                    if node_id not in mapped_nodes:
                        return node_id, string_index
        return None, None

    @staticmethod
    def _get_node_position(child_morphism: Morphism, begin_at: float, padding: float) -> (float, float):

        pocket = padding * 2
        width = (max(len(child_morphism.domain.objects), len(child_morphism.codomain.objects)) * pocket)

        if type(child_morphism).__name__ == "IdentityMorphism":
            center = width / 2
        else:
            if len(child_morphism.domain.objects) >= len(child_morphism.codomain.objects):
                child_strings = Diagram.make_strings(child_morphism.domain.objects)
            else:
                child_strings = Diagram.make_strings(child_morphism.codomain.objects)
            x_positions = Diagram._compute_string_spacing(strings=child_strings, padding=padding)

            center = sum(x_positions) / len(x_positions)

        return begin_at + center, width

    @staticmethod
    def _compute_string_spacing(strings: list, padding: float):
        pocket = padding * 2
        return [Diagram._get_node_position(child_morphism=s, begin_at=(i * pocket), padding=padding)[0]
                for i, s in enumerate(strings)]

    @staticmethod
    def to_graph_from_slices(slices: list, padding: float = 0.5, offset: float = 0):
        # number of nodes = len(domain) + 1 + len(codomain)
        # number of edges = len(domain) + len(codomain)
        # slices should always alternate: (identity morphisms, named morphisms)

        Position = collections.namedtuple("Position", ["y", "x"])
        Node = collections.namedtuple("Node",
                                      ["id", "name", "index_position", "position", "type", "width"])  # morphisms
        Edge = collections.namedtuple("Edge", ["id", "source_node", "target_node", "name",
                                               "source_position", "target_position"])  # composition

        nodes = dict()
        edges = dict()
        previous_slice = []
        mapped_nodes = []
        max_col = -1
        max_row = len(slices)
        for rank, slice in enumerate(slices):
            curr_offset = offset
            for col, m in enumerate(slice):
                max_col = max(col, max_col)
                x_pos, _width = Diagram._get_node_position(child_morphism=m, begin_at=curr_offset, padding=padding)
                curr_offset = x_pos + _width / 2

                _node_id = "{}_({})_({})".format(m.name, rank, col)
                _index_position = Position(y=rank, x=col)._asdict()
                _position = Position(y=rank, x=x_pos)._asdict()
                _type = type(m).__name__

                if _type == "IdentityMorphism":
                    _name = m.domain.name
                else:
                    _name = m.name

                # if _type == "NamedMorphism" and "\u03C4" in _name:  # "\u03C4" is Greek letter tau for braids, hacky :(
                #     continue

                node = Node(id=_node_id, name=_name, index_position=_index_position, position=_position, type=_type, \
                            width=_width)._asdict()

                nodes[_node_id] = node

                if rank == 0:  # ignore first row, these are inputs
                    continue

                prev_rank = rank - 1
                domain_strings = Diagram.make_strings(m.domain.objects)

                for i, string in enumerate(domain_strings):
                    _source_node_id, _mapped_string_ind = Diagram._find_morphism_with_string(morphisms=previous_slice,
                                                                                             morphisms_rank=prev_rank,
                                                                                             string=string,
                                                                                             mapped_nodes=mapped_nodes)

                    # look one row above, braids don't have nodes
                    # if _source_node_id is None or "\u03C4" in _source_node_id:
                    #     _source_node_id, _mapped_string_ind = Diagram._find_morphism_with_string(
                    #         morphisms=slices[prev_rank - 1],
                    #         morphisms_rank=prev_rank - 1,
                    #         string=string,
                    #         mapped_nodes=mapped_nodes)

                    if _source_node_id is None:
                        print("Cannot find source node for {}!".format(_node_id))
                        continue

                    _source_node = nodes[_source_node_id]

                    if _source_node["type"] == "IdentityMorphism":
                        mapped_nodes.append(_source_node_id)
                    elif _source_node["type"] == "NamedMorphism":
                        # handle when morphism has a codomain string that is the same as another morphism in that slice
                        _node_id_with_index = "{}_({})".format(_source_node_id, _mapped_string_ind)
                        mapped_nodes.append(_node_id_with_index)

                    _target_node = _node_id
                    _edge_id = "[{}]*[{}]_{}".format(_source_node_id, _target_node, string.domain.name)
                    _name = string.domain.name

                    if type(m).__name__ == "IdentityMorphism" and _source_node["type"] == "NamedMorphism":
                        source_position = Position(x=_position["x"], y=rank - 1)._asdict()  # use current x position
                        target_position = Position(x=_position["x"], y=rank)._asdict()  # use own x_position
                    elif type(m).__name__ == "NamedMorphism" and _source_node["type"] == "IdentityMorphism":
                        source_position = Position(x=_source_node["position"]["x"],
                                                   y=rank - 1)._asdict()  # use current x position
                        target_position = Position(x=_source_node["position"]["x"],
                                                   y=rank)._asdict()  # use own x_position
                    else:
                        source_position = Position(x=_source_node["position"]["x"], y=rank - 1)._asdict()
                        target_position = Position(x=_position["x"], y=rank)._asdict()  # use own x_position

                    edge = Edge(id=_edge_id, source_node=_source_node_id, target_node=_target_node, name=_name,
                                target_position=target_position, source_position=source_position)._asdict()
                    edges[_edge_id] = edge

            previous_slice = slice
            size = (max_row, max_col + 1)
        return nodes, edges, size

    def as_graph(self):
        slices = self.slices()
        nodes, edges, size = self.to_graph_from_slices(slices=slices)
        return nodes, edges, size

    @staticmethod
    def _build_node_colormap(nodes):
        # import random
        # r = lambda: str(random.randint(0, 255))
        # color = "rgb({}, {}, {})".format(r(), r(), r())
        # rgb = [[x, y, z] for x in range(256) for y in range(256) for z in range(256)]
        # import matplotlib.pyplot as plt
        from colorhash import ColorHash
        node_names = [n["name"] for _, n in nodes.items() if n["type"] == "IdentityMorphism"]
        uniq_node_names = set(node_names)
        # color_func = plt.cm.get_cmap("tab20b", len(uniq_node_names))
        # colors = ["rgb({}, {}, {})".format(color_func(i)[0] * 255,
        #                                    color_func(i)[1] * 255,
        #                                    color_func(i)[2] * 255)
        #           for i, _ in enumerate(uniq_node_names)]
        colors = ["rgb({}, {}, {})".format(ColorHash(x).rgb[0],
                                           ColorHash(x).rgb[1],
                                           ColorHash(x).rgb[2])
                  for i, x in enumerate(uniq_node_names)]
        colormap = dict(zip(uniq_node_names, colors))
        return colormap

    @staticmethod
    def to_vis_from_graph(nodes: dict, edges: dict, filename: str or None, scale: int, label_strings: bool = True,
                          color_nodes: bool = False):

        colormap = Diagram._build_node_colormap(nodes)

        cyto = []
        max_y_position = max([n["position"]["y"] for _, n in nodes.items()])

        for _, node in nodes.items():
            c = dict()
            if node["type"] == "NamedMorphism" and "\u03C4" in node["name"]:
                node["shape"] = "round-rectangle"
                node["opacity"] = 1
                node["label"] = "\u03C4"
                node["height"] = scale / 4
                node["width"] = node["width"] * scale
                node["color"] = "white"
            elif node["type"] == "NamedMorphism":
                node["shape"] = "round-rectangle"
                node["opacity"] = 1
                node["label"] = node["name"]
                node["height"] = scale / 2
                node["width"] = node["width"] * scale
                node["color"] = "#dcdcdc"
            elif node["type"] == "IdentityMorphism" and node["name"] == "[]":
                # node["label"] = ""
                node["height"] = 0
                node["width"] = 0
                node["opacity"] = 0
            elif node["type"] == "IdentityMorphism":
                if label_strings or node["position"]["y"] == 0 or node["position"]["y"] == max_y_position:
                    node["label"] = node["name"]
                    node["shape"] = "ellipse"
                    node["opacity"] = 1
                    node["height"] = scale / 4
                    node["width"] = scale / 4
                else:
                    # node["label"] = node.pop("name")
                    node["shape"] = "ellipse"
                    node["opacity"] = 1
                    node["height"] = 0.5
                    node["width"] = 0.5

                # import random
                # r = lambda: str(random.randint(0,255))
                # node["color"] = "rgb({}, {}, {})".format(r(),r(),r())

                if color_nodes:
                    node["color"] = colormap[node["name"]]
                else:
                    node["color"] = "#dcdcdc"
            pos = {key: val * scale for key, val in node["position"].items()}
            c["data"] = node
            c["position"] = pos
            c["group"] = "nodes"
            cyto.append(c)

        for _, edge in edges.items():
            c = dict()
            target_center = nodes[edge["target_node"]]["position"]["x"]
            source_center = nodes[edge["source_node"]]["position"]["x"]
            edge["source"] = edge.pop("source_node")
            edge["target"] = edge.pop("target_node")
            edge["label"] = edge.pop("name")
            edge["target_position"] = "{} {}".format((edge["target_position"]["x"] - target_center) * scale, "-50%")
            edge["source_position"] = "{} {}".format((edge["source_position"]["x"] - source_center) * scale, "50%")
            c["data"] = edge
            c["group"] = "edges"
            cyto.append(c)

        cyto_dump = json.dumps(cyto)
        if filename is not None:
            with open(filename, "w") as outfile:
                json.dump(json.loads(cyto_dump), outfile)
        return cyto

    def to_vis(self, filename: str or None, scale: int = 100, label_strings: bool = True, color_nodes: bool = False):
        # tailored to cytoscape for now
        nodes, edges, _ = self.as_graph()
        return self.to_vis_from_graph(nodes=nodes, edges=edges, filename=filename, scale=scale,
                                      label_strings=label_strings, color_nodes=color_nodes)

    def to_array(self):
        nodes, _, size = self.as_graph()
        return Diagram.graph_to_array(nodes=nodes, size=size)

    @staticmethod
    def graph_to_array(nodes: dict, size: tuple):
        myarray = np.zeros(size)
        for _, node in nodes.items():
            name = node["name"]
            value = abs(hash(name)) % (10 ** 8)  # hash function to convert name to integer
            row, col = node["index_position"]["y"], node["index_position"]["x"]

            counter = list(range(int(node["width"] if node["width"] > 1 else node["width"])))
            while counter:
                shift = counter.pop(0)
                myarray[row][col + shift] = value
        return myarray.astype('uint8')

    def to_json(self):
        return json.dumps(self.slices(), default=MonoidalCategory.json_encoder)

    def inverse(self):
        # Make sure the inverse is the same type as the original morphism
        return Diagram(morphism=self.morphism.inverse())

    @staticmethod
    def asymm_diff(base: list, elements: list):
        diff = []
        base_copy = base.copy()  # to not overwrite in place
        for el in elements:
            if el in base_copy:
                base_copy.remove(el)
            else:
                diff.append(el)
        return diff

    @staticmethod
    def make_strings(objects: List[Object or MonoidalObject]):
        strings = []
        for el in objects:
            if isinstance(el, Object):
                el = MonoidalObject(el)  # make all strings based on MonoidalObjects
                strings.append(IdentityMorphism(el))
            elif isinstance(el, MonoidalObject):
                for o in el.objects:
                    o = MonoidalObject(o)  # make all strings based on MonoidalObjects
                    strings.append(IdentityMorphism(o))
            else:
                return strings
        return strings

    @staticmethod
    def _add_to_left_side_(index_to_add: int, target_list_length: int) -> bool:
        # index:    [-3 -2  -1  0   1   2]
        # target:   [_  A   B   C   D   _]
        #
        # index_to_add = 2, target_list_length = 4
        #
        # available space on left is -3
        # available space on right is 2

        ind_left = 0 - index_to_add - 1
        ind_right = target_list_length - index_to_add

        if abs(ind_left) < ind_right:
            return True  # add to left
        elif abs(ind_left) > ind_right:
            return False  # add to right
        else:
            return False  # default: add to right

    @staticmethod
    def yarn_pattern(cloth: list, yarn: list):
        # For example,
        # top:      [f] where f: foo --> A @ B @ C @ D
        # bottom:   [g] where g: A @ B @ E @ C --> bar
        # =>
        # [(E, False)]  "add E to the right of f"

        yarn_pattern = []
        diff = Diagram.asymm_diff(base=cloth, elements=yarn)
        for d in diff:
            # bottom: [A B (E) C] => 2
            ind_bottom = yarn.index(d)

            if Diagram._add_to_left_side_(index_to_add=ind_bottom, target_list_length=len(cloth)):
                yarn_pattern.append((d, True))  # True means add to left-side
            else:
                yarn_pattern.append((d, False))  # default: add to right-side
        return yarn_pattern

    @staticmethod
    def weave_pattern(cloth: list, yarn: list, in_place: bool = True):
        # For example,
        # top:      [A B C D]
        # bottom:   [A B E C]
        # =>
        # top:      [A B C D E]
        # bottom:   [A B E C D]

        if in_place:
            cloth_new = cloth
        else:
            cloth_new = cloth.copy()

        diff = Diagram.asymm_diff(base=cloth_new, elements=yarn)
        for d in diff:
            # bottom: [A B (E) C] => 2
            ind_bottom = yarn.index(d)

            if Diagram._add_to_left_side_(index_to_add=ind_bottom, target_list_length=len(cloth_new)):
                cloth_new.insert(0, d)  # add to left
            else:
                cloth_new.insert(len(cloth_new), d)  # default: add to right
        return cloth_new

    @staticmethod
    def _swap_(lst: list, pos1: int, pos2: int):
        lst[pos1], lst[pos2] = lst[pos2], lst[pos1]
        return lst

    @staticmethod
    def _make_unique_(x: list):
        x_counter = collections.Counter(x)
        x_counter_list = dict()
        for k, v in x_counter.items():
            x_counter_list[k] = list(range(v))

        x_uniq = []
        x_uniq_map = dict()
        for o in x:
            ind = x_counter_list[o][0]
            del x_counter_list[o][0]
            label = "{}_{}".format(o.name, ind)
            x_uniq.append(label)
            x_uniq_map[label] = o
        return x_uniq, x_uniq_map

    @staticmethod
    def compute_swaps(a: list, b: list):
        # Apply swaps to `a` to reach `b`

        if len(a) != len(b):
            raise ValueError("Both lists must be equal lengths!")

        if collections.Counter(a) != collections.Counter(b):
            raise ValueError("Both lists must contain the same values!")

        a_uniq, a_uniq_map = Diagram._make_unique_(x=a)
        b_uniq, b_uniq_map = Diagram._make_unique_(x=b)

        swaps = []
        new_a = a_uniq.copy()  # fix b
        elements = a_uniq
        while elements:
            for el in elements:
                index_a = new_a.index(el)
                value_b = b_uniq[index_a]
                if el == value_b:
                    elements.remove(el)
                    break  # if they are in the same position, move on
                else:
                    index_b = b_uniq.index(el)
                    compare_indices = index_a - index_b
                    if compare_indices < 0:  # if negative, means index_a is to the left index_b
                        delta = 1  # move to the right
                        swaps.append((a_uniq_map[el], a_uniq_map[new_a[index_a + delta]]))  # swaps are (left, right)
                    elif compare_indices > 0:  # if positive, means index_a is the the right of index_b
                        delta = -1  # move to the left
                        swaps.append((a_uniq_map[new_a[index_a + delta]], a_uniq_map[el]))  # swaps are (left, right)
                    else:  # which should be never
                        delta = 0
                    new_a = Diagram._swap_(new_a, index_a, index_a + delta)  # only change list a
        return swaps

    @staticmethod
    def add_braids(from_diagram, to_diagram) -> list:
        # find braids
        top = from_diagram.codomain.objects
        bottom = to_diagram.domain.objects

        try:
            swaps = Diagram.compute_swaps(top, bottom)
        except ValueError:
            raise ValueError("Can not compute swaps for composing diagrams")

        braids = []
        for a, b in swaps:
            braids.append(SymmetricMonoidalCategory.swap(a, b))
        braids = SymmetricMonoidalCategory.simplify(braids)

        # insert monoidal morphisms with braid in between top and bottom diagram
        diagram_with_braids = [from_diagram]
        objects_above = from_diagram.morphism.codomain.objects
        for braid in braids:
            # scan codomain objects in pairs
            braid_ind = -1
            for obj_l, obj_r in zip(objects_above, objects_above[1:]):
                braid_ind += 1
                if obj_l == braid.domain.objects[0] and obj_r == braid.domain.objects[1]:  # if object pairs match braid
                    break

            tensor = []
            for curr_ind, obj in enumerate(objects_above):
                if braid_ind == curr_ind:
                    tensor.append(braid)
                elif braid_ind + 1 == curr_ind:
                    continue
                else:
                    tensor.append(IdentityMorphism(obj))

            new_diagram = Diagram(MonoidalMorphism(*tensor))
            diagram_with_braids.append(new_diagram)
            objects_above = new_diagram.morphism.codomain.objects

        diagram_with_braids.append(to_diagram)
        return diagram_with_braids

    def compose(self, other):
        # compose := self * other
        # compose(self, other) = self -> other
        # self first, then other

        if isinstance(other, Diagram):
            new_self = self
            new_other = other

            # weave other-up first
            cloth_strings = Diagram.make_strings(self.codomain)
            yarn_strings = Diagram.make_strings(other.domain)
            pattern = Diagram.yarn_pattern(cloth=cloth_strings, yarn=yarn_strings)
            for (m, left_side) in pattern:
                if left_side:
                    new_self = Diagram(MonoidalMorphism(m, new_self.morphism))
                else:
                    new_self = Diagram(MonoidalMorphism(new_self.morphism, m))

            # weave self-down next
            cloth_strings = Diagram.make_strings(other.domain)
            yarn_strings = Diagram.make_strings(self.codomain)
            pattern = Diagram.yarn_pattern(cloth=cloth_strings, yarn=yarn_strings)
            for (m, left_side) in pattern:
                if left_side:
                    new_other = Diagram(MonoidalMorphism(m, new_other.morphism))
                else:
                    new_other = Diagram(MonoidalMorphism(new_other.morphism, m))

            morphism_with_braids = Diagram.add_braids(from_diagram=new_self, to_diagram=new_other)
            return StringDiagram(morphism_with_braids)
        else:
            raise TypeError("Can only compose Diagram with other Diagrams!")

    def slices(self):
        return [Diagram.make_strings(self.domain.objects),
                self.morphism.morphisms if isinstance(self.morphism, MonoidalMorphism) else [self.morphism],
                Diagram.make_strings(self.codomain.objects)]

    def tensor(self):
        raise NotImplementedError

    def draw(self):
        raise NotImplementedError

    def __mul__(self, other):
        return self.compose(other)

    def __str__(self):
        return self.name

    def __iter__(self):
        yield "name", self.name
        yield "domain", self.domain.objects
        yield "codomain", self.codomain.objects
        yield "linear_syntax", self.linear_syntax


class StringDiagram:
    def __init__(self, diagrams: List[Diagram], name: str or None = None):

        morphisms = [d.morphism for d in diagrams]
        for current, following in zip(morphisms, morphisms[1:]):
            if current.codomain != following.domain:
                raise ValueError("Cannot compose {} with {}!".format(current.name, following.name))

        self._diagrams = tuple(diagrams)
        if name is None:
            self.name = " * ".join([d.name for d in self.diagrams])
        else:
            self.name = name

    @property
    def diagrams(self):
        return list(self._diagrams)

    @property
    def linear_syntax(self):
        return " * ".join([d.name for d in self.diagrams])

    @property
    def morphisms(self):
        return [d.morphism for d in self.diagrams]

    @property
    def domain(self):
        return self.diagrams[0].domain

    @property
    def codomain(self):
        return self.diagrams[-1].codomain

    @staticmethod
    def weave(diagrams: list):
        new_diagrams = []
        top_d = diagrams.pop(0)
        for bottom_d in diagrams:
            merged_sd = top_d * bottom_d
            new_diagrams = new_diagrams + merged_sd.diagrams
            top_d = new_diagrams.pop(-1)
        new_diagrams.append(top_d)
        return new_diagrams

    def compose(self, other):
        if not isinstance(other, (Diagram, StringDiagram)):
            raise TypeError("Can only compose StringDiagram with Diagram or StringDiagram!")

        if isinstance(other, StringDiagram):
            other_diagrams = other.diagrams
        else:
            other_diagrams = [other]
        self_diagrams = self.diagrams

        to_be_woven = self_diagrams + other_diagrams

        # weave down
        woven_down = StringDiagram.weave(diagrams=to_be_woven)  # weave down first
        woven_down.reverse()  # flip
        woven_down = [d.inverse() for d in woven_down]  # flip domain and codomains

        # weave up
        woven_up = StringDiagram.weave(diagrams=woven_down)  # weave up
        woven_up.reverse()  # flip back
        woven_up = [d.inverse() for d in woven_up]  # flip back domain and codomains

        new_diagrams = woven_up
        return StringDiagram(new_diagrams)

    def as_morphism(self):
        return CompositeMorphism(self.morphisms)

    def to_json(self):
        return json.dumps(self.slices(), default=MonoidalCategory.json_encoder)

    def as_graph(self):
        slices = self.slices()
        return Diagram.to_graph_from_slices(slices)

    def to_vis(self, filename: str, scale: int = 100, label_strings: bool = True, color_nodes: bool = False):
        nodes, edges, _ = self.as_graph()
        return Diagram.to_vis_from_graph(nodes=nodes, edges=edges, filename=filename, scale=scale,
                                         label_strings=label_strings, color_nodes=color_nodes)

    def to_array(self):
        nodes, _, size = self.as_graph()
        return Diagram.graph_to_array(nodes=nodes, size=size)

    def slices(self):
        slices = sum([d.slices()[1:] for d in self.diagrams], [])  # remove domain slice for every diagram
        # slices = [m.morphisms if isinstance(m, MonoidalMorphism) else [m] for m in self.morphisms]
        slices.insert(0, Diagram.make_strings(self.domain.objects))
        # slices.append(Diagram.make_strings(self.codomain.objects))
        return slices

    def __mul__(self, other):
        return self.compose(other)

    def __len__(self):
        return len(self.diagrams)

    def __str__(self):
        return self.name
