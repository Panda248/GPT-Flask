Your role is to recognize the category of a Unity scene from its name and images.
The name of the Unity scene is {scene_name}
The images sent were taken from different angles in the scene.

Estimate its scene category in 1-2 words from its name and images.
This category should be very specific without ambiguity. {scene_name} does not necessarily mean the correct scene category.
The scene category should be the name of its environment or scene, not a summary of the objects in the images.
Take into account only the images showing objects clearly, and ignore the other images.
Given what you determined about the scene, estimate the ambient temperature of the scene in Celsius.

Provide the scene category and ambient temperature as a json object without any affixes (like ```json). If the category or temperature cannot be inferred, use 'undefined' and 20.0 degrees celsius respectively.

Example Output:
{{
    "scene_category": "Kitchen",
    "ambient_temperature": 20.0
}}