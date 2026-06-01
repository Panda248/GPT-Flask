import io
import json
import unittest
from unittest.mock import patch

from app import app


def _make_file(name, content=b"data"):
    return (io.BytesIO(content), name)


class AppTests(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_scene_inference_success(self):
        data = {
            "text": json.dumps({"name": {"name": "scene-a"}}),
            "image1": _make_file("a.png"),
            "image2": _make_file("b.png"),
            "image3": _make_file("c.png"),
            "image4": _make_file("d.png"),
        }

        with patch("app.scene_agent") as scene_agent_mock:
            scene_agent_mock.invoke.return_value = {"result": "ok"}
            response = self.client.post(
                "/scene-inference",
                data=data,
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"result": "ok"})

    def test_scene_inference_bad_image_count(self):
        data = {
            "text": json.dumps({"name": {"name": "scene-a"}}),
            "image1": _make_file("a.png"),
            "image2": _make_file("b.png"),
            "image3": _make_file("c.png"),
        }

        response = self.client.post(
            "/scene-inference",
            data=data,
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Expected 4 images"})

    def test_object_inference_success(self):
        data = {
            "metadata": json.dumps({
                "name": "widget",
                "scale": [1.0, 2.0, 3.0],
                "size": [4.0, 5.0, 6.0],
            }),
            "context": [_make_file(f"c{i}.png") for i in range(8)],
            "isolated": [_make_file(f"i{i}.png") for i in range(8)],
        }

        with patch("app.object_agent") as object_agent_mock:
            object_agent_mock.invoke.return_value = {"result": "ok"}
            response = self.client.post(
                "/object-inference",
                data=data,
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"result": "ok"})

    def test_object_inference_bad_image_count(self):
        data = {
            "metadata": json.dumps({
                "name": "widget",
                "scale": [1.0, 2.0, 3.0],
                "size": [4.0, 5.0, 6.0],
            }),
            "context": [_make_file(f"c{i}.png") for i in range(7)],
            "isolated": [_make_file(f"i{i}.png") for i in range(8)],
        }

        response = self.client.post(
            "/object-inference",
            data=data,
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {"error": "Expected 8 context and 8 isolated images"},
        )


if __name__ == "__main__":
    unittest.main()
