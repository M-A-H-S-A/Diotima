import json
import re

def extract_json_string(text):
    """
    Extracts the first valid-looking JSON object or array from the text.
    """
    match = re.search(r'\{[\s\S]*\}|\[[\s\S]*\]', text)
    return match.group(0) if match else None


def sanitize_json_string(s):
    """
    Cleans common LLM JSON issues:
    - Removes trailing commas
    - Strips whitespace
    - Balances braces/brackets
    """
    if not s:
        return s

    # Remove trailing commas before } or ]
    s = re.sub(r",(\s*[}\]])", r"\1", s)

    # Balance curly braces
    open_braces = s.count("{")
    close_braces = s.count("}")
    if open_braces > close_braces:
        s += "}" * (open_braces - close_braces)
    elif close_braces > open_braces:
        s = "{" * (close_braces - open_braces) + s

    # Balance square brackets
    open_brackets = s.count("[")
    close_brackets = s.count("]")
    if open_brackets > close_brackets:
        s += "]" * (open_brackets - close_brackets)
    elif close_brackets > open_brackets:
        s = "[" * (close_brackets - open_brackets) + s

    return s.strip()


def safe_json_parse(text):
    """
    Attempts to safely parse a JSON string from any LLM output.
    """
    json_str = extract_json_string(text)
    if not json_str:
        raise ValueError("No JSON object/array found in LLM output.")

    cleaned_str = sanitize_json_string(json_str)
    try:
        return json.loads(cleaned_str)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"JSON parsing failed: {e}\n--- Cleaned JSON ---\n{cleaned_str}"
        )


def parse_questions_response(response_json):
    """
    Parses the LLM output for a dictionary of questions, grouped by Bloom's level.
    Works across different LLM providers.
    """
    if not isinstance(response_json, dict) or 'choices' not in response_json or not response_json['choices']:
        raise ValueError("Invalid response_json format received by output_processor.")

    message = response_json['choices'][0]['message']['content']

    parsed_data = safe_json_parse(message)
    questions_data = parsed_data.get('questions', parsed_data)

    if not isinstance(questions_data, dict):
        raise ValueError("Expected a JSON object with Bloom levels as keys.")

    return questions_data


def parse_qna_response(response_json):
    """
    Parses the LLM output for a single Q&A pair (expected to be a JSON object).
    Works across different LLM providers.
    """
    if not isinstance(response_json, dict) or 'choices' not in response_json or not response_json['choices']:
        raise ValueError("Invalid response_json format received by output_processor.")

    message = response_json['choices'][0]['message']['content']
    return safe_json_parse(message)



def save_questions_with_content(questions_data, filename):
    """
    Saves a dictionary of questions (grouped by Bloom's level)
    and their source content to a JSON file.

    Args:
        questions_data (dict): The dictionary containing questions and
                               source text, typically from parse_questions_response.
        filename (str): The name of the output file (e.g., "generated_questions_with_sources.json").
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(questions_data, file, indent=4, ensure_ascii=False)
        print(f"Successfully saved questions with content to {filename}")
    except IOError as e:
        print(f"Error saving file: {e}")

# Example of how to use this function after getting a response from the LLM:
#
# # Assuming you have a response from the LLM after calling build_questions_prompt
# llm_response_json = {
#     "choices": [
#         {
#             "message": {
#                 "content": """
#                 {
#                   "questions": {
#                     "Remembering": [
#                       {
#                         "question": "What is genetic engineering?",
#                         "source_text": "Genetic engineering is the alteration of an organism’s genotype using recombinant DNA technology to modify an organism’s DNA to achieve desirable traits."
#                       },
#                       {
#                         "question": "What is a genetically modified organism (GMO)?",
#                         "source_text": "The organism that receives the recombinant DNA is called a genetically modified organism (GMO)."
#                       }
#                     ]
#                   }
#                 }
#                 """
#             }
#         }
#     ]
# }
#
# # 1. Parse the LLM's response
# parsed_questions = parse_questions_response(llm_response_json)
#
# # 2. Save the parsed questions and content to a file
# save_questions_with_content(parsed_questions, "questions_with_content.json")