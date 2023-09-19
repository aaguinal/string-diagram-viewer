# String Diagram Visualization Library

This is a library that provides constructs for monoidal categories and string diagrams from category theory. Category theory is a mathematical theory under abstract algebra that helps encode how things relate to one another through functions, maps, or relationships \[1, 2, 3, 4\]. Category theory was initially introduced as a way to transfer theorems between algebra and topology in order to study the field of algebraic topology. In doing so, it provides a mathematical language that lifts many mathematical and non-mathematical concepts to this notion of maps between entities and compositions of maps. This provides a generic theory of open and interconnected systems often found in AI, IoT, and other process-based systems. String diagrams are a graphical syntax for a mathematical structure defined in category theory \[5\].

![img](img/string_diagram_demo.gif)

The purpose of this tool is to generate and visualize arrows in freely generated monoidal categories at will. This tool allows you to specify a list of arrows, including their domain and codomain, in the order you would like to compose them. An internal algorithm can determine how to tensor identity morphisms to simulate dragging the strings up and down such that composition is satisfied. The arrows must adhere to the for JSON schema shown [here](https://gitlab.jhuapl.edu/categorytheory/compositional-systems-analysis/-/blob/ac756d362b4f700bf5928d639ee912072e70edf5/wsgi/static/data/examples/demo.json). Each key-value pair in the JSON as arrows in a monoidal category. The algorithm that handles composition with dangling objects, or strings, includes the following steps: 

1. Backward pass. Weave input strings of each arrow from bottom-up 
2. Forward pass. Weave output strings of each arrow from top-down 
3. Add braids. Add braids, or string swaps (τ), in case the order of the tensor product is not compatible for composition. 
4. Compose. Chain the blocks from top-down. This constructs the string diagram.

### Some applications of string diagrams

_For robot program modeling_
* Aguinaldo, A., Bunker, J., Pollard, B., Shukla, A., Canedo, A., Quiros, G., & Regli, W. (2021). RoboCat: A Category Theoretic Framework for Robotic Interoperability Using Goal-Oriented Programming. IEEE Transactions on Automation Science and Engineering, 1–9. https://doi.org/10.1109/TASE.2021.3094055

_For AI planning (PDDL plan modeling)_
* Aguinaldo, A., & Regli, W. (2021). A Graphical Model-Based Representation for PDDL Plans using Category Theory Anonymous Anonymous Affiliation. ICAPS 2021 Workshop XAIP. www.aaai.org

_For assembly and processing planning_
* Breiner, S., Jones, A., & Subrahmanian, E. (2016). Categorical models for process planning. 1–35.
* Master, J., Patterson, E., Yousfi, S., & Canedo, A. (2019). String Diagrams for Assembly Planning. http://arxiv.org/abs/1909.10475

_For control theory_
* Fong, B., Sobociski, P., & Rapisarda, P. (2016). A categorical approach to open and interconnected dynamical systems. Proceedings - Symposium on Logic in Computer Science, 05-08-July(1), 495–504. https://doi.org/10.1145/2933575.2934556

## Getting Started
Requirements: Python >3.7

1. Clone the repository
2. `cd` into `compositional-systems-analysis/`
3. Create Python virtual environment `python3 -m venv venv` and activate `source venv/bin/activate` (in unix-based OS)
4. Install requirements `pip install -r requirements.txt`
5. Run app `python3 run_vis.py`

## Running the tests

Run the following in the top-level directory
```
python3 -m unittest discover -s categorytheory/tests -v
```

## Roadmap

Here are some planned improvements, in no particular order:
* Support planar deformation \[5\] (sliding boxes past each other)
* Better decomposition navigation
* Updating visualization formats (coloring nodes) without re-drawing


## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions
available, see the [tags on this
repository](https://gitlab.jhuapl.edu/categorytheory/compositional-systems-analysis/-/tags).

## License

This project is licensed under [Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0).
Copyright under Johns Hopkins University Applied Physics Laboratory.

## References

[1] Barr, M., & Wells, C. (1995). Category Theory for Computing Sciences. In 2nd Ed. Prentice Hall International (UK) Ltd.,. https://doi.org/10.1192/bjp.112.483.211-a

[2] Leinster, T. (2016). Basic Category Theory. Cambridge University Press. https://arxiv.org/pdf/1612.09375.pdf

[3] Fong, B., & Spivak, D. I. (2018). Seven sketches in compositionality: An invitation to applied category theory. Cambridge University Press.

[4] Baez, J., & Stay, M. (2011). Physics, topology, logic and computation: A Rosetta Stone. Lecture Notes in Physics, 813, 95–172. https://doi.org/10.1007/978-3-642-12821-9_2

[5] Selinger, P. (n.d.). A survey of graphical languages for monoidal categories. 1–63.
