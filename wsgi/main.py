import os
from functools import reduce

import numpy as np
from matplotlib import pyplot as plt
import pydash
from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from categorytheory.Diagram import Diagram
from categorytheory.MonoidalCategory import MonoidalObject, NamedMorphism

templates = Jinja2Templates(directory="wsgi/templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="wsgi/static"), name="static")


@app.get("/")
async def read_root(request: Request, response_class=HTMLResponse):
    return templates.TemplateResponse("index.html", {"request": request, "message": "hello"})


@app.get("/echo/{message}")
async def read_data(request: Request, message: str):
    return message


@app.post("/build_string_diagram")
def build_string_diagram(request: Request, data: dict = Body(...)):
    morphisms_dict = pydash.get(data, "morphisms", dict())
    morphisms_to_compose = pydash.get(data, "compose", [])
    scale = pydash.get(data, "scale", 100)
    labels = pydash.get(data, "labels", True)
    color = pydash.get(data, "color", False)

    # convert to category theory morphisms
    to_compose = []
    for key in morphisms_to_compose:
        value = pydash.get(morphisms_dict, key, None)

        if value is None:
            msg = "Cannot find morphism with key: {}!".format(key)
            print(msg)
            return 500, msg

        name = pydash.get(value, "name")
        inputs = MonoidalObject(*pydash.get(value, "input", []))
        outputs = MonoidalObject(*pydash.get(value, "output", []))

        diagram = Diagram(NamedMorphism(domain=inputs, codomain=outputs, name=name))

        to_compose.append(diagram)

    try:
        sd = reduce(lambda x, y: x * y, to_compose)
    except ValueError:
        return 500

    return sd.to_vis(filename=None, scale=scale, label_strings=labels, color_nodes=color)


@app.post("/to_image")
def get_string_diagram_to_image(request: Request, data: dict = Body(...)):
    morphisms_dict = pydash.get(data, "morphisms", dict())
    morphisms_to_compose = pydash.get(data, "compose", [])

    # convert to category theory morphisms
    to_compose = []
    for key in morphisms_to_compose:
        value = pydash.get(morphisms_dict, key, None)

        if value is None:
            msg = "Cannot find morphism with key: {}!".format(key)
            print(msg)
            return 500, msg

        name = pydash.get(value, "name")
        inputs = MonoidalObject(*pydash.get(value, "input", []))
        outputs = MonoidalObject(*pydash.get(value, "output", []))

        diagram = Diagram(NamedMorphism(domain=inputs, codomain=outputs, name=name))

        to_compose.append(diagram)

    sd = reduce(lambda x, y: x * y, to_compose)
    myarray = sd.to_array()
    myarray = myarray / np.amax(myarray) * 255
    myarray.astype('uint8')
    plt.imsave(os.path.join(os.path.dirname(os.path.realpath(__file__)), "static", "downloads", "image.png"), myarray)
    return 200


def find_root(tree: dict):
    children = sum([pydash.get(value, "compose", []) for _, value in tree])
    for k, _ in tree:
        if k not in children:
            return k
