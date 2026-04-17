from google.genai import types

BASE_URL = "https://renkaat247.fi/chat-api/"

SYSTEM_PROMPT = """You are a car enthusiast, and a tyre expert. You have a deep understanding of different types of tyres, seasonal variations, load indexes, speed ratings, and OEM fitments of all brand/model cars in the world.
</role>

<goal>
Your ultimate goal is to go online and detect the information about OEM fitments for specific brand, model, and year of vehicles.
</goal>

<output_requirements>
- Provide a JSON output with the following format:
{
    \"predicted_oem_front_tyre_size\": <string>,
    \"oem_front_tyre_sizes\": [<string>, ...],
    \"predicted_oem_rear_tyre_size\": <string>,
    \"oem_rear_tyre_sizes\": [<string>, ...],
    \"confidence\": <float between 0 and 1>,
    \"wheel_diameter_inches\": <integer>,
    \"rim_type_estimate\": <string>,
    \"load_index\": <integer>,
    \"speed_rating\": <string>,
}
</output_requirements>"""

USER_PROMPT = """<input>
Brand: {brand}
Model: {model}
Year: {year}
</input>
"""

GEMINI_MODEL = "gemini-3.1-flash-lite-preview"

RESPONSE_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    required=[],
    properties={
        "predicted_oem_front_tyre_size": types.Schema(
            type=types.Type.STRING,
            description="The most likely OEM front tyre size for the given brand, model, and year of the vehicle, use format 'width/heightRdiameter' e.g., '205/55R16'."
        ),
        "oem_front_tyre_sizes": types.Schema(
            type=types.Type.ARRAY,
            description="A list of all possible OEM front tyre sizes for the given brand, model, and year of the vehicle, use format 'width/heightRdiameter' e.g., '205/55R16'.",
            items=types.Schema(
                type=types.Type.STRING,
                description="An OEM front tyre size for the given brand, model, and year of the vehicle, use format 'width/heightRdiameter' e.g., '205/55R16'."
            )
        ),
        "predicted_oem_rear_tyre_size": types.Schema(
            type=types.Type.STRING,
            description="The most likely OEM rear tyre size for the given brand, model, and year of the vehicle, use format 'width/heightRdiameter' e.g., '205/55R16'."
        ),
        "oem_rear_tyre_sizes": types.Schema(
            type=types.Type.ARRAY,
            description="A list of all possible OEM rear tyre sizes for the given brand, model, and year of the vehicle, use format 'width/heightRdiameter' e.g., '205/55R16'.",
            items=types.Schema(
                type=types.Type.STRING,
                description="An OEM rear tyre size for the given brand, model, and year of the vehicle, use format 'width/heightRdiameter' e.g., '205/55R16'."
            )
        ),
        "confidence": types.Schema(
            type=types.Type.NUMBER,
            description="The confidence level of the predicted tyre sizes."
        ),
        "wheel_diameter_inches": types.Schema(
            type=types.Type.INTEGER,
            description="The diameter of the wheel in inches."
        ),
        "rim_type_estimate": types.Schema(
            type=types.Type.STRING,
            description="An estimate of the rim type."
        ),
        "load_index": types.Schema(
            type=types.Type.INTEGER,
            description="The load index of the tyre."
        ),
        "speed_rating": types.Schema(
            type=types.Type.STRING,
            description="The speed rating of the tyre."
        )
    }
)
