from flask import Flask, Response, jsonify, request
from werkzeug.datastructures import FileStorage
from langchain.messages import AIMessage, ContentBlock, HumanMessage
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from base64 import b64encode
import json


app = Flask(__name__)

load_dotenv()

object_model=init_chat_model("openai:gpt-4o", temperature=0.2, max_tokens=1024)
scene_model=init_chat_model("openai:gpt-4o", temperature=0.2, max_tokens=1024)

def get_images_from_request(prefix: str, count: int) -> list:
    images = [
        img for img in
        (request.files.get(f"{prefix}{i}") for i in range(1, count + 1))
        if img is not None
    ]
    return images


def save_images_if_testing(images: list[FileStorage], prefix: str):
    if app.config["DEBUG"]:
        for image in images:
            image.save(f"temp_images/{prefix}/{image.filename}")


def construct_content_blocks(prompt: str, 
                             images: list[FileStorage]) -> list[ContentBlock]:
    content : list[ContentBlock]= [{"type": "text", "text": prompt}]
    for image in images:
        b64 = b64encode(image.read()).decode("utf-8")
        content.append({
            "type": "image",
            "base64": b64,
            "mime_type": "image/jpeg"
        })
        image.seek(0)
    return content


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


def create_response(message: AIMessage) -> Response:
    return Response(message.text, status=200, mimetype="application/json")


def close_images(images: list[FileStorage]):
    for image in images:
        image.close()


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
    raw = request.form["jsonText"] if "jsonText" in request.form else None
    if not raw:
        print("error: missing jsonText in form data")
        return Response("Missing jsonText in form data", 
                        status=400, mimetype="text/plain")
    try:
        data_obj = json.loads(raw)
    except json.JSONDecodeError:
        print("error: invalid JSON for metadata")
        return Response("Invalid JSON for metadata", 
                        status=400, mimetype="text/plain")
    scene_name = data_obj.scene_name if "scene_name" in data_obj else None

    images = get_images_from_request("scene", 4)
    save_images_if_testing(images, "scene")
    if len(images) != 4:
        print(f"error: expected 4 images but got {len(images)}")
        return Response(f"Expected 4 images, got {len(images)}", 
                        status=400, mimetype="text/plain")

    prompt = loadPrompt("scene.md", scene_name=scene_name)
    # print(f"prompt: {prompt}")

    message = HumanMessage(
        content_blocks=construct_content_blocks(prompt, images)
    ) 
    result = (
        object_model.invoke([message])
        if not app.config["DEBUG"] else AIMessage(content="kitchen") 
    )
    print(f"result: {result.content}")

    close_images(images)
    return create_response(result)


@app.route("/object-material-inference", methods=["POST"])
def object_material_inference():
    raw = request.form.get("jsonText")
    print(f"raw jsonText: {raw}")
    if not raw:
        print("error: missing jsonText in form data")
        return Response("Missing jsonText in form data", 
                        status=400, mimetype="text/plain")
    try:
        data_obj = json.loads(raw)
    except json.JSONDecodeError:
        print("error: invalid JSON for metadata")
        return Response("Invalid JSON for metadata", 
                        status=400, mimetype="text/plain")
    name = data_obj["name"] if "name" in data_obj else None
    scale = data_obj["scale"] if "scale" in data_obj else None
    size = data_obj["size"] if "size" in data_obj else None
    scene_category = (
        data_obj["scene_category"] if "scene_category" in data_obj else None
    )
    context_images = get_images_from_request("context", 8)
    isolated_images = get_images_from_request("iso", 8)
    save_images_if_testing(context_images, "object")
    save_images_if_testing(isolated_images, "object")

    if len(context_images) != 8 or len(isolated_images) != 8:
        print("error: expected 8 context and 8 isolated images but got "
              f" {len(context_images)} context and "
              f"{len(isolated_images)} isolated")
        return Response("error: Expected 8 context and 8 isolated images "
                        f"but got {len(context_images)} context and "
                        f"{len(isolated_images)} isolated",
                        status=400,
                        mimetype="text/plain")

    prompt = loadPrompt("objectmaterial.md", 
                        user_prompt="", 
                        object_name=name, 
                        scale=scale, 
                        size=size, 
                        scene_category=scene_category,
                        len_isolated_images=8,
                        len_scene=8)
    # print(f"prompt: {prompt}")

    message = HumanMessage(content_blocks=
        construct_content_blocks(prompt, context_images + isolated_images));
    result = (
        object_model.invoke([message]) 
        if not app.config["DEBUG"] 
        else AIMessage(
            content=open("object_material_stub.json").read()
        )
    )
    print(f"result: {result.content}")

    close_images(context_images + isolated_images)
    return Response(result.text, status=200, mimetype="application/json")

