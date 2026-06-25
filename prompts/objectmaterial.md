Your role is to recognize the contexts of a Unity gameobject from its name, size, position, and images and infer the material properties of the object.
The user prompt is {user_prompt}. If the user prompt is not empty, conduct the below estimation with the highest importance on the user prompt.
The scene category of the Unity scene is {scene_category}.
The object name in the Unity scene is {object_name}.
The size of the object in the scene is {size} in a meter unity. It is not decided with value of this size vector is the width, height, or depth. This size is a dimension of the dominant surface of the object. For example, if the object is a table with legs, the value is the size of the tabletop.
The sent images comprise two sets. The first {len_isolated_images} are isolated images that show an object of interest in the center part from different angles. The other {len_scene} images are scene images that show the same object in the scene from different angles.

Estimate its object category in 1-3 words from its name, size, position, and images. However, if {object_name} sounds like a boundary surface (e.g., 'refrigerator' is better than 'appliance" in terms of clarity). {object_name} is not necessarily the correct object category.
If there are multiple options for the object category, choose the one that is most likely to exist in {scene_category}. Try not to choose a category that is not likely to exist in {scene_category}.
When you check the scene images, estimate the object category of only the object in the center of the scene iamges and most resembles the object in the isolated images.
Take into account only the images showing some objects clearly, and ignore the other images.
Take into account the object's authenticity based on whether it is being used in a physically plausible way in the scene images and whether its size roughly matches the typical size of its object category that humans use in everyday environments. This size check should not be too strict. If this object is not authentic, include a word to describe the authenticity (e.g., 'miniature' if the object is too small) in the estimated object category.
Position information can be used to estimate the object category,  especially if it has an ambiguous name and shape.
Do not estimate the object category from the light and reflective conditions because the images are taken from various lighting conditions.

If the object is a boundary surface, it is likely that one axis of {size} is too small in Unity. In that case, estimate the object size by replacing only that axis value witha  typical value for the object category in meters and provide a reason in one sentence. Return the same value as {size} for the estimated size in the other cases. Not that you should return the value in a string format like '1.0,1.0,1.0'. For example, if the thickness of the room floor is too small, replace it with a typical value for the room floor.
Estimate its material category in 1 word from its isolated images and object category. If the object comprises multiple materials, choose the most dominant material. This material category should be as specific as possible, not a general term. (e.g., 'iron' or 'steel' should be used rather than 'metal' in terms of concreteness). If the object is not authentic, estimate the material category based on the object's authenticity. If the sobject seems like a boundary surface and is textureless, estimate the material that is likely to be present in the {scene_category} based on its surface color.

Now, determine the following material properties based on your estimates.
Heat capacity in joules per gram, thermal conductivity in watts per meter celsius, total mass of the object in grams and the initial temperature of the object in celsius. 
Give these properties in decimal format. If it is a whole number, add a trailing 0 (i.e. 1.0 rather than 1)
Additionally, determine whether or not the object could be a heat source. If so, estimate its in heat generation rate in joules per second as well as whether the object can be turned on/off and if it is initially on at the beginning of the scene. If you determined the object cannot be a heat source, leave heat generation rate as 0.

If you cannot estimate all or parts of the material properties for some reason, assign 0 for those values. Do not do this for mass or specific heat as these are not possible.

Additionally, provide brief reasons for the object category, material, heat generation rate, and whether or not it is a heat source.

Provide the object category, object category justification, material category, material category justification, whether or not its a heat source, justification for why it is or isnt a heat source, heat generation rate, heat generation rate justification, toggleable, initially on, heat capacity, thermal conductivity, mass, initial temperature, and material justification in plaintext JSON format without any affixes (e.g. markdown wrappers like ```json). All structured outputs should be provided.

Example output:
{{
  "object_category": "coffee maker",
  "object_category_justification": "The name 'KA_CoffeeMaker_V1' and the object's appearance in the images suggest it is a coffee maker, which is common in kitchens.",
  "material_category": "plastic",
  "material_category_justification": "The isolated images show a texture and color typical of plastic, which is common for coffee makers.",
  "is_heat_source": true,
  "heat_source_justification": "Coffee makers are typically heat sources as they heat water to brew coffee.",
  "heat_generation_rate": 1000.0,
  "heat_generation_rate_justification": "A typical coffee maker generates around 1000 watts (joules per second) when in use.",
  "toggleable": true,
  "initially_on": false,
  "heat_capacity": 1.5,
  "thermal_conductivity": 0.2,
  "mass": 2000.0,
  "initial_temperature": 20.0
}}