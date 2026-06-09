from flask import Flask, jsonify, request
from langchain.messages import ContentBlock, HumanMessage
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from base64 import b64encode
import json

app = Flask(__name__)

load_dotenv()

object_model=init_chat_model("openai:gpt-4o", temperature=0.2, max_tokens=1024)
scene_model=init_chat_model("openai:gpt-4o", temperature=0.2, max_tokens=1024)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/test")
def test():
    result = object_model.invoke([HumanMessage(content="Output Hello, World")])
    return result.content

# Producing scene category
@app.route("/scene-inference", methods=["POST"])
def scene_inference():
    raw_text = request.form["jsonText"] if "jsonText" in request.form else None
    print(f"raw_text: {raw_text}")
    text_obj = json.loads(raw_text) if raw_text else None
    scene_name = text_obj.get("scene_name") if text_obj else None

    # print(list(request.files))
    images = [
        img for img in (request.files.get(f"scene{i}") for i in range(1, 5))
        if img is not None
    ]
    
    if app.config["TESTING"]:
        for image in images:
            image.save(f"temp_images/scene/{image.filename}") 

    if len(images) != 4:
        print("error: expected 4 images but got", len(images))
        return jsonify({"error": "Expected 4 images"}), 400

    prompt = loadPrompt("scene.md", scene_name=scene_name)
    print(f"prompt: {prompt}")

    # print(b64encode(request.files["scene1"].read()))
    # request.files["scene1"].seek(0)

    content :list[ContentBlock]= [{"type": "text", "text": prompt}]
    for image in images:
        b64 = b64encode(image.read()).decode("utf-8")
        content.append({
            "type": "image",
            "base64": b64,
            "mime_type": "image/jpeg"
        })

    message = HumanMessage(content_blocks=content)

    result = object_model.invoke([message])
    print(f"result: {result.content}")

    jsoned = jsonify(result.content)
    
    for image in images:
        image.close()

    return jsoned


# endpoint for processing object data
# returns whether object is heat source
# Temperature range, material properties (conductive/insulate)
# heat change over time
@app.route("/object-inference", methods=["POST"])
def object_inference():
    # Get Textual Information
    raw_meta = request.form.get("jsonText")

    if not raw_meta:
        print("error: missing jsonText in form data")
        return jsonify({"error": "Missing jsonText in form data"}), 400

    # print(f"raw_meta: {raw_meta}")
    try:
        meta_payload = json.loads(raw_meta)
    except json.JSONDecodeError:
        print("error: invalid JSON for metadata")
        return jsonify({"error": "Invalid JSON for metadata"}), 400
    name = meta_payload.get("name")
    scale = meta_payload.get("scale")
    size = meta_payload.get("size")
    scene_category = meta_payload.get("scene_category")

    # Get Image Data
    images = request.files
    
    context_images = [
        img for img in (images.get(f"context{i}") for i in range(1, 9))
        if img is not None
    ]

    isolated_images = [
        img for img in (images.get(f"iso{i}") for i in range(1, 9))
        if img is not None
    ]

    if app.config["TESTING"]:
        for image in context_images:
            image.save(f"temp_images/object/{image.filename}")

        for image in isolated_images:
            image.save(f"temp_images/object/{image.filename}")

    if len(context_images) != 8 or len(isolated_images) != 8:
        print("error: expected 8 context and 8 isolated images but got", len(context_images), "context and", len(isolated_images), "isolated")
        return jsonify({"error": "Expected 8 context and 8 isolated images"}), 400

    prompt = loadPrompt("object.md", 
                        user_prompt="", 
                        object_name=name, 
                        scale=scale, 
                        size=size, 
                        scene_category=scene_category,
                        len_isolated_images=8,
                        len_scene=8)

    print(f"prompt: {prompt}")

    content :list[ContentBlock]= [{"type": "text", "text": prompt}]
    for image in context_images:
        b64 = b64encode(image.read()).decode("utf-8")
        content.append({
            "type": "image",
            "base64": b64,
            "mime_type": "image/jpeg"
        })
        image.seek(0)

    for image in isolated_images:
        b64 = b64encode(image.read()).decode("utf-8")
        content.append({
            "type": "image",
            "base64": b64,
            "mime_type": "image/jpeg"
        })
        image.seek(0)

    message = HumanMessage(content_blocks=content);

    result = object_model.invoke([message])
    print(f"result: {result.content}")

    jsoned = jsonify(result.content)

    for image in context_images + isolated_images:
        image.close()

    return jsoned

@app.route("/object-material-inference", methods=["POST"])
def object_material_inference():
    # Get Textual Information
    raw_meta = request.form.get("jsonText")

    if not raw_meta:
        print("error: missing jsonText in form data")
        return jsonify({"error": "Missing jsonText in form data"}), 400

    # print(f"raw_meta: {raw_meta}")
    try:
        meta_payload = json.loads(raw_meta)
    except json.JSONDecodeError:
        print("error: invalid JSON for metadata")
        return jsonify({"error": "Invalid JSON for metadata"}), 400
    name = meta_payload.get("name")
    scale = meta_payload.get("scale")
    size = meta_payload.get("size")
    scene_category = meta_payload.get("scene_category")

    # Get Image Data
    images = request.files
    
    context_images = [
        img for img in (images.get(f"context{i}") for i in range(1, 9))
        if img is not None
    ]

    isolated_images = [
        img for img in (images.get(f"iso{i}") for i in range(1, 9))
        if img is not None
    ]

    if app.config["TESTING"]:
        for image in context_images:
            image.save(f"temp_images/object/{image.filename}")

        for image in isolated_images:
            image.save(f"temp_images/object/{image.filename}")

    if len(context_images) != 8 or len(isolated_images) != 8:
        print("error: expected 8 context and 8 isolated images but got", len(context_images), "context and", len(isolated_images), "isolated")
        return jsonify({"error": "Expected 8 context and 8 isolated images"}), 400

    prompt = loadPrompt("objectmaterial.md", 
                        user_prompt="", 
                        object_name=name, 
                        scale=scale, 
                        size=size, 
                        scene_category=scene_category,
                        len_isolated_images=8,
                        len_scene=8)

    print(f"prompt: {prompt}")

    content :list[ContentBlock]= [{"type": "text", "text": prompt}]
    for image in context_images:
        b64 = b64encode(image.read()).decode("utf-8")
        content.append({
            "type": "image",
            "base64": b64,
            "mime_type": "image/jpeg"
        })
        image.seek(0)

    for image in isolated_images:
        b64 = b64encode(image.read()).decode("utf-8")
        content.append({
            "type": "image",
            "base64": b64,
            "mime_type": "image/jpeg"
        })
        image.seek(0)

    message = HumanMessage(content_blocks=content);

    result = object_model.invoke([message])
    print(f"result: {result.content}")

    jsoned = jsonify(result.content)

    for image in context_images + isolated_images:
        image.close()

    return jsoned

def loadPrompt(filename : str, **kwargs) -> str:
    with open(f"prompts/{filename}", "r") as f:
        output = f.read()
        f.close()
        return output.format(**kwargs)


def parse_vector(value: str) -> list[float]:
    cleaned = value.strip()
    if not (cleaned.startswith("(") and cleaned.endswith(")")):
        raise ValueError("Expected format: (x,y,z)")

    parts = [part.strip() for part in cleaned[1:-1].split(",")]
    if len(parts) != 3:
        raise ValueError("Expected three comma-separated numbers")

    try:
        return [float(part) for part in parts]
    except ValueError as exc:
        raise ValueError("All values must be floats") from exc
