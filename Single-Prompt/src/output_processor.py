import json
import re

def basic_json_cleanup(bad_json):
    """
    Fix common JSON mistakes:
    - Missing commas between objects in lists
    - Too many closing braces/brackets
    - Trimmed start/end
    """
    # Fix missing commas between objects in arrays
    cleaned = re.sub(r'}\s*{', '},\n{', bad_json)

    # Remove excessive closing brackets at the end (e.g., }}}}})
    while cleaned.strip().endswith('}}}}'):
        cleaned = cleaned.strip()[:-1]

    # Ensure top-level object starts and ends with braces
    if not cleaned.strip().startswith('{'):
        cleaned = '{' + cleaned
    if not cleaned.strip().endswith('}'):
        cleaned += '}'

    return cleaned

def parse_and_save_response(response_json, output_file):
    if not isinstance(response_json, dict) or 'choices' not in response_json or \
       not response_json['choices'] or 'message' not in response_json['choices'][0] or \
       'content' not in response_json['choices'][0]['message']:
        raise ValueError("Invalid response_json format received by output_processor.")

    message = response_json['choices'][0]['message']['content']

    json_match = re.search(r'```json\s*(\{.*?\})\s*```', message, re.DOTALL)
    if json_match:
        json_string = json_match.group(1)
    else:
        json_match = re.search(r'(\{.*\})', message, re.DOTALL)
        json_string = json_match.group(0) if json_match else message.strip()

    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f" Initial parse failed: {e}")
        print("Attempting basic cleanup...")

        cleaned_json = basic_json_cleanup(json_string)

        try:
            data = json.loads(cleaned_json)
            print("Successfully parsed after cleanup.")
        except json.JSONDecodeError as e2:
            print(f"Still failed to parse: {e2}")
            print("\n--- JSON Preview Around Error ---")
            print(cleaned_json[max(0, e2.pos - 80):min(len(cleaned_json), e2.pos + 80)])
            print("\n--- Full (cleaned) JSON ---")
            print(cleaned_json[:1000] + ('...' if len(cleaned_json) > 1000 else ''))
            raise

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f" Q&As and rubrics saved to {output_file}")
