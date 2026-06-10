Your role is to estimate the material properties of an object.
You are given the json text for an object inside a Unity scene that describes its inferred category, material, and size. The json is below:
{object_json}
Estimate heat capacity in joules per gram, thermal conductivity in watts per meter celsius, total mass of the object in kilograms, and initial temperature of the object given the scene category {scene_category}
If you cannot estimate the material properties for some reason, assign the value as 0.

Provide the heat capacity, thermal conductivity, mass, and temperature in a JSON format without any affixes. All structured outputs should be provided.