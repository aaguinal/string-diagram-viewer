const host = "127.0.0.1"
const port = 8000

function buildUrl (url) {
    return "http://" + host + ":" + port + "/" + url
}

var app = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        message: 'Hello, world!',
        default_example: 'default',  // must be key in examples.json
        cy_style: null,
        diagram: null,
        total_morphisms: 0,
        examples: [],
        composition: [],
        example: null,
        root_key: null,
        level: 0,
        maxlevel: null,
        cached_style: null,
        percent_effected: 0,
        number_effected: 0,
        hoverover: false,
        unhighlightColor: '#dcdcdc',
        highlightColor: '#ffc04c',
        selected_name: this.default_example,
        scale: 100,
        labels: false,
        color: false,
        loading: false,
        file: null,
        valid_schema: ["name", "input", "output", "compose", "level"]
    },
    mounted() {
        this.echo('ayooo');
        this.getCyStyle();
        this.getExamples();
    },
    watch: {
        diagram: function (elements) {
            // When the diagram elements change, redraw the diagram
            this.drawDiagram(elements);
        },

        labels: function() {
            // When labels are turned on and off, reconstruct diagram
            if (this.composition.length > 0) {
                this.constructDiagram(this.composition);
            }
        },

        color: function() {
            // When labels are turned on and off, reconstruct diagram
            if (this.composition.length > 0) {
                this.constructDiagram(this.composition);
            }
        },

        scale: function() {
            // When labels are turned on and off, reconstruct diagram
            if (this.composition.length > 0) {
                this.constructDiagram(this.composition);
            }
        },

        composition: function(composition) {
            // When composition is modified, draw
            if (composition.length > 0) {
                this.constructDiagram(composition);
            }
        },

        hoverover: function(ele) {
            if (this.hoverover) {
                // console.log(this.cy.style())

                let highlightRgb = this.hexToRGB(this.highlightColor)
                let highlighted_morphisms = _.filter(this.cy.elements().filter('node[type = "NamedMorphism"]'), function (m) {
                    return m.style()["background-color"] === highlightRgb;
                })
                this.percent_effected = Math.round((highlighted_morphisms.length / this.total_morphisms) * 100);
                this.number_effected = highlighted_morphisms.length
            } else {
                this.percent_effected = 0
                this.number_effected = 0
            }
        }
    },
    methods: {
        parseJSON(data) {
            return JSON.parse(JSON.stringify(data))
        },

        echo(yodel) {
            let url = buildUrl('echo/' + yodel);
            axios.get(url, {mode: 'no-cors'}).then((response) => {
                this.message = response.data;
            }).catch(error => {
                toastr.error("Cannot connect to server!");
            });
        },

        getCyStyle() {
            let url = buildUrl("static/data/cy-style.json");
            axios.get(url, {mode: 'no-cors'})
                .then((response) => {
                    this.cy_style = this.parseJSON(response.data)
                });
        },

        constructDiagram(compose){
            this.loading = true
            let payload = {
                morphisms: this.parseJSON(this.example),
                compose: compose,
                scale: parseInt(this.scale),
                labels: this.labels,
                color: this.color
            };
            let url = buildUrl("build_string_diagram");
            axios.post(url, payload)
                .then((response) => {
                    if (response.data === 500) {
                        toastr.error("Cannot construct string diagram!")
                        this.loading = false
                        this.diagram = null
                    } else {
                        this.diagram = this.parseJSON(response.data)
                        this.total_morphisms = _.filter(this.diagram, function(o) {
                            return o.data.type==="NamedMorphism";
                        }).length
                        this.loading = false
                    }
                });

            url = buildUrl("to_image");
            axios.post(url, payload);
        },

        drawDiagram(elements){
            this.cy = cytoscape({
                container: document.getElementById("cy"),
                boxSelectionEnabled: false,
                autounselectify: true,
                hideEdgesOnViewport: true,
                pixelRatio: 1,
                layout: {
                    name: 'preset'
                },
                style: this.cy_style,
                elements: elements
            });
            let original_colors = {}

            this.cy.pon('tap', 'node[type = "NamedMorphism"]')
                .then(function(evt){
                    let id = evt.target.id();
                    let node = this.app.filterNodesById(id)[0];  // assumes there's only one and it's the first one [0]
                    let key = _.findKey(this.app.example, ['name', node.data.label])

                    // update level state
                    let node_level = this.app.example[key].level
                    if (node_level === this.app.maxlevel) {
                        this.app.level = node_level
                    } else {
                        this.app.level = node_level + 1
                        // +1 because we are rendering the decomposition of the node
                    }
                    console.log("``````````CLICKED " + node.data.label + "``````````")
                    // console.debug("Level after click: " + this.app.level)

                    let composition = this.app.example[key].compose
                    if (composition.length > 0) {
                        this.app.composition = composition;  // get decomposition using .compose
                    } else {
                        // if there's no decomposition, re-render the diagram
                        this.app.level = node_level // undo level increment
                        this.app.constructDiagram(this.app.composition)  // TODO: fix so it doesn't need to re-render
                    }
                });

            this.cy.elements().filter('node[type = "IdentityMorphism"]').bind('tapdragover', (evt) => {
                this.hoverover = true;
                let node = evt.target;
                let components = node.successors();
                original_colors[node.data().id] = node.style()["background-color"]
                for (let i = 0; i < components.length; i++) {
                    original_colors[components[i].data().id] = components[i].style()["background-color"]
                }

                node.style({'background-color': this.highlightColor});
                components.style({'background-color': this.highlightColor});
            });

            this.cy.elements().filter('node[type = "IdentityMorphism"]').bind('tapdragout', (evt) => {
                this.hoverover = false;
                let node = evt.target;
                let components = node.successors();
                node.style({'background-color': original_colors[node.data().id]});
                for (let i = 0; i < components.length; i++) {
                    components[i].style({'background-color': original_colors[components[i].data().id]});
                }

            });
        },

        getExamples() {
            let url = buildUrl("static/data/examples.json");
            axios.get(url, {mode: 'no-cors'})
                .then((response) => {
                    this.examples = this.parseJSON(response.data)
                    let default_example = this.examples[this.default_example];
                    this.setExample(default_example);
                });
        },

        setExample(item) {
            this.selected_name = item.name;
            let url = buildUrl("static/data/examples/" + item.file);
            axios.get(url, {mode: 'no-cors'})
                .then((response) => {
                    this.example = this.parseJSON(response.data)
                    this.root_key = this.getRoot(this.example);
                    this.level = 0;
                    this.maxlevel = this.getMaxLevel();
                    this.composition = [this.root_key];
                })
                .catch(function() {
                    toastr.error("No file found for " + this.example.name)
                });
        },

        getCompositionForLevel(desired_level) {
            let new_level = desired_level
            if (desired_level === 0) {
                this.composition = [this.root_key];
            } else {
                // Handle substitution of compositions
                // `this.level` provides the degree of substitution
                let arrows_at_level = this.example[this.root_key].compose
                let prev_arrows_at_level = arrows_at_level  // hold to revert if something breaks
                for (let lvl = 1; lvl < desired_level; lvl++) {
                    console.debug("lvl: " + lvl)
                    prev_arrows_at_level = arrows_at_level

                    try {
                        arrows_at_level = _.map(arrows_at_level, function(a){
                            return this.app.example[a].compose
                        })
                    } catch (TypeError) {
                        console.error("Not all arrows have decomposition!")
                        toastr.error("Not all arrows have decomposition! Moving to Level " + (new_level + 1))
                        // +1 because zero-indexed, but the UI is one-indexed
                        arrows_at_level = prev_arrows_at_level
                        break
                    }

                    new_level = lvl + 1
                    console.debug("new_level: " + new_level)
                }
                this.composition = _.flatten(arrows_at_level);
            }
            console.debug("return new_level: " + new_level)
            return new_level
        },

        incrementLevel() {
            console.log("``````````INCREMENTING LEVEL``````````")
            // console.debug("Current level: " + this.level)
            // console.debug("Max level: " + this.maxlevel)
            let desired_level
            if (this.level !== this.maxlevel) {
                desired_level = this.level + 1;
            } else {
                desired_level = this.level
            }
            // console.debug("incrementLevel() before -- this.level: " + this.level)
            // console.debug("incrementLevel() -- desired_level: " + desired_level)
            this.level = this.getCompositionForLevel(desired_level);
            // console.debug("incrementLevel() after -- this.level: " + this.level)
        },

        decrementLevel() {
            console.log("``````````DECREMENTING LEVEL``````````")
            // console.debug("Current level: " + this.level)
            let desired_level
            if (this.level !== 0 ){
                desired_level = this.level - 1;
            } else {
                desired_level = this.level
            }
            // console.debug("decrementLevel() before -- this.level: " + this.level)
            // console.debug("decrementLevel() -- desired_level: " + desired_level)
            this.level = this.getCompositionForLevel(desired_level);
            // console.debug("decrementLevel() after -- this.level: " + this.level)
        },

        getRoot(spec) {
            return _.findKey(spec, ['level', 0])
        },

        getMaxLevel() {
            var levels = _.map(this.example, 'level');
            return _.max(levels)
        },

        getArrowsAtLevel(spec, level){
            var arrows = _.filter(spec, ['level', level])
            return _.keys(arrows)
        },

        filterNodesById(id) {
            return _.filter(this.diagram, function(o) {
                return o.data.id === id;
            })
        },

        savePNG(){
            window.saveAs(this.cy.png({ full: true }), "graph.png");
        },

        hexToRGB(h) {
            let r = 0, g = 0, b = 0;

            // 3 digits
            if (h.length == 4) {
                r = "0x" + h[1] + h[1];
                g = "0x" + h[2] + h[2];
                b = "0x" + h[3] + h[3];

                // 6 digits
            } else if (h.length == 7) {
                r = "0x" + h[1] + h[2];
                g = "0x" + h[3] + h[4];
                b = "0x" + h[5] + h[6];
            }

            return "rgb("+ +r + "," + +g + "," + +b + ")";
        },

        dragover(event) {
            event.preventDefault();
            // Add some visual fluff to show the user can drop its files
            event.target.style.backgroundColor = "#95b8ca";
            event.target.style.opacity = 0.6;
        },
        dragleave(event) {
            event.preventDefault();
            event.target.style.backgroundColor = ""
            event.target.style.opacity = ""
        },
        drop(event) {
            event.preventDefault();
            event.target.style.backgroundColor = ""
            event.target.style.opacity = ""

            let filelist = event.dataTransfer.files;
            var reader = new FileReader();

            // Describe function to run after reading file
            reader.onload = (evt) => {
                evt.preventDefault();
                let val = evt.target.result;

                // Validate input
                try {  // Check if JSON
                     JSON.parse(val)
                } catch (e) {
                    toastr.error("Must be in JSON format!")
                    return
                }

                let check = JSON.parse(val);
                let keys_match = true;
                _.forEach(check, (data, key) => {  // Check if all object keys match schema
                    keys_match = _.isEqual(_.keys(data).sort(), this.valid_schema.sort());
                })
                if (!keys_match){
                    toastr.error("Every object must have keys " + JSON.stringify(this.valid_schema));
                    return
                }

                // Assign contents as example to show
                this.example = check;

                // Build diagram
                this.composition = [this.getRoot(this.example)]
                this.constructDiagram(this.composition)
                this.root_key = this.getRoot(this.example);  // For navigation
                this.selected_name = filelist[0].name
            };

            reader.readAsText(filelist[0]);
        }

    }
});
