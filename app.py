from flask import Flask, jsonify, request
import json

app = Flask(__name__)

# test dependencies
try :
    import dotenv
    print("dotenv exists")
except ImportError:
    print("dotenv does not exist")
try :
    import openai
    print("openai exists")
except ImportError:
    print("openai does not exist")
try :
    import langchain
    print("langchain exists")
except ImportError:
    print("langchain does not exist")

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

@app.route("/scene-inference", methods=["POST"])
def scene_inference():
    prompt = ""

    images = []
    for _, storage in request.files.items():
        images.append({
            "filename": storage.filename,
            "content_type": storage.content_type,
            "data": storage.read(),
        })

    if len(images) != 4:
        return jsonify({"error": "Expected 4 images"}), 400

    text_raw = request.form.get("text") or request.form.get("metadata") or ""
    try:
        text_payload = json.loads(text_raw) if text_raw else {}
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON for text payload"}), 400

    payload = {
        "images": images,
        "text": text_payload,
    }

    result = scene_agent.invoke({"prompt": prompt, "data": payload})
    return jsonify(result)

@app.route("/object-inference", methods=["POST"])
def object_inference():
    prompt = ""

    context_images = request.files.getlist("context")
    isolated_images = request.files.getlist("isolated")

    if not context_images or not isolated_images:
        all_images = list(request.files.values())
        context_images = all_images[:8]
        isolated_images = all_images[8:16]

    if len(context_images) != 8 or len(isolated_images) != 8:
        return jsonify({"error": "Expected 8 context and 8 isolated images"}), 400

    def pack_images(storages):
        return [
            {
                "filename": storage.filename,
                "content_type": storage.content_type,
                "data": storage.read(),
            }
            for storage in storages
        ]

    def parse_vector(value):
        if isinstance(value, list) and len(value) == 3:
            return [float(x) for x in value]
        if isinstance(value, str):
            cleaned = value.strip().lstrip("(").rstrip(")")
            parts = [p.strip() for p in cleaned.split(",") if p.strip()]
            if len(parts) == 3:
                return [float(p) for p in parts]
        raise ValueError("Invalid vector")

    raw_meta = request.form.get("metadata")
    if raw_meta:
        try:
            meta_payload = json.loads(raw_meta)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON for metadata"}), 400
        name = meta_payload.get("name")
        scale = meta_payload.get("scale")
        size = meta_payload.get("size")
    else:
        name = request.form.get("name")
        scale = request.form.get("scale")
        size = request.form.get("size")

    try:
        scale_vec = parse_vector(scale) if scale is not None else None
        size_vec = parse_vector(size) if size is not None else None
    except ValueError:
        return jsonify({"error": "Invalid scale or size vector"}), 400

    payload = {
        "context_images": pack_images(context_images),
        "isolated_images": pack_images(isolated_images),
        "metadata": {
            "name": name,
            "scale": scale_vec,
            "size": size_vec,
        },
    }

    result = object_agent.invoke({"prompt": prompt, "data": payload})
    return jsonify(result)