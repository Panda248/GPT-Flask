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

    images = list(request.files.values())

    if len(images) != 4:
        return jsonify({"error": "Expected 4 images"}), 400

    raw_text = request.form.get("json")
    text_payload = json.loads(raw_text) if raw_text else None
    payload = {
        "images": images,
        "text": text_payload,
    }

    result = scene_agent.invoke({"prompt": prompt, "data": payload})
    jsoned = jsonify(result)
    return jsoned if jsoned else jsonify({"error": "No result from agent"}), 500

@app.route("/object-inference", methods=["POST"])
def object_inference():
    prompt = ""

    images = request.files
    context_images = [images.get(f"context{i}") for i in range(0, 16, 2)]
    isolated_images = [images.get(f"iso{i}") for i in range(1, 16, 2)]

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

    raw_meta = request.form.get("json")
    if raw_meta:
        try:
            meta_payload = json.loads(raw_meta)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON for metadata"}), 400
        name = meta_payload.get("name")
        scale = meta_payload.get("scale")
        size = meta_payload.get("size")
    else:
        print("nothing from json")

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
    jsoned = jsonify(result)
    return jsoned if jsoned else jsonify({"error": "No result from agent"}), 500