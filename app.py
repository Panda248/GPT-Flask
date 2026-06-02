from flask import Flask, jsonify, request
import json

app = Flask(__name__)

from langchain.agents import create_agent
from openai import OpenAI

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

model=init_chat_model("openai:gpt-4o", temperature=0.2)

scene_agent = create_agent(
    model,
    system_prompt="Your role is "
)

object_agent = create_agent(
    model,
    system_prompt="Your role is"
)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Endpoint for processing scene data and producing scene category
@app.route("/scene-inference", methods=["POST"])
def scene_inference():
    prompt = ""

    # print(list(request.files))
    images = [request.files.get(f"scene{i}") for i in range(1, 5, 1)]
    # print(images)

    for image in images:
        if image is not None:
            image.save(f"temp_images/scene/{image.filename}") 

    if len(images) != 4:
        print("error: expected 4 images but got", len(images))
        return jsonify({"error": "Expected 4 images"}), 400

    raw_text = request.form["jsonText"] if "jsonText" in request.form else None
    print(f"raw_text: {raw_text}")
    text_payload = json.loads(raw_text) if raw_text else None
    payload = {
        "images": images,
        "text": text_payload,
    }

    result = scene_agent.invoke({"prompt": prompt, "data": payload})
    jsoned = jsonify(result)
    if not jsoned:
        print("error: no result from scene agent")
    return jsoned if jsoned else jsonify({"error": "No result from agent"}), 500


# endpoint for processing object data
# returns whether object is heat source
# Temperature range, material properties (conductive/insulate)
# heat change over time
@app.route("/object-inference", methods=["POST"])
def object_inference():
    prompt = ""

    images = request.files
    print(list(request.files.values()))
    context_images = [images.get(f"context{i}") for i in range(1, 9, 1)]
    isolated_images = [images.get(f"iso{i}") for i in range(1, 9, 1)]

    for image in context_images:
        if image is not None:
            image.save(f"temp_images/object/{image.filename}")
    for image in isolated_images:
        if image is not None:
            image.save(f"temp_images/object/{image.filename}")

    print(context_images)
    print(isolated_images)
    if len(context_images) != 8 or len(isolated_images) != 8:
        print("error: expected 8 context and 8 isolated images but got", len(context_images), "context and", len(isolated_images), "isolated")
        return jsonify({"error": "Expected 8 context and 8 isolated images"}), 400
    
    def parse_vector(value):
        if isinstance(value, list) and len(value) == 3:
            return [float(x) for x in value]
        if isinstance(value, str):
            cleaned = value.strip().lstrip("(").rstrip(")")
            parts = [p.strip() for p in cleaned.split(",") if p.strip()]
            if len(parts) == 3:
                return [float(p) for p in parts]
        raise ValueError("Invalid vector")

    raw_meta = request.form.get("jsonText")
    print(f"raw_meta: {raw_meta}")
    try:
        meta_payload = json.loads(raw_meta)
    except json.JSONDecodeError:
        print("error: invalid JSON for metadata")
        return jsonify({"error": "Invalid JSON for metadata"}), 400
    name = meta_payload.get("name")
    scale = meta_payload.get("scale")
    size = meta_payload.get("size")

    try:
        scale_vec = parse_vector(scale) if scale is not None else None
        size_vec = parse_vector(size) if size is not None else None
    except ValueError:
        print("error: invalid scale or size vector")
        return jsonify({"error": "Invalid scale or size vector"}), 400

    payload = {
        "context_images": context_images,
        "isolated_images": isolated_images,
        "metadata": {
            "name": name,
            "scale": scale_vec,
            "size": size_vec,
        },
    }

    result = object_agent.invoke({"prompt": prompt, "data": payload})
    jsoned = jsonify(result)
    if not jsoned:
        print("error: no result from object agent")
    return jsoned if jsoned else jsonify({"error": "No result from agent"}), 500