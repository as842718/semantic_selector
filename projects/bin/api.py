from flask import Flask, request, jsonify, make_response, g
from semantic_selector import ml_model
from semantic_selector import datasource

import os
import yaml

app = Flask(__name__)


def get_model():
    if not hasattr(g, 'model') or g.model is None:
        label_file = "../../data/label_grouping_example.yml"
        label_file = os.path.join(os.path.dirname(__file__), label_file)
        with open(label_file) as f:
            label_grouping = yaml.load(f.read())
        g.model = ml_model.LsiModel(grouping=label_grouping)
    return g.model


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'model') and g.model is not None:
        datasource.InputTags.cleanup()


@app.route("/api/inference", methods=['POST'])
def inference():
    if request.headers['Content-Type'] != 'application/json':
        return make_response("Content-Type must be application/json", 400)

    if "html" not in request.json.keys():
        err_message = 'request body json must contain "html" attributes'
        return make_response(err_message, 400)

    target_tag = request.json["html"]
    model = get_model()
    estimated_label = model.inference_html(target_tag)
    res = {"label": estimated_label}
    return jsonify(res)