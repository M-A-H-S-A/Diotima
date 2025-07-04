import json
import requests
import os
from openai import OpenAI

# Always get base dir of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")  # /data root

# --------------- Helpers ---------------

def find_subtopic_text(topic_dict, subtopic_name):
    """
    Recursively search for subtopic_name in topic_dict and return its 'text'.
    """
    if not isinstance(topic_dict, dict):
        return None

    if subtopic_name in topic_dict:
        subtopic_data = topic_dict[subtopic_name]
        if isinstance(subtopic_data, dict) and "text" in subtopic_data:
            return subtopic_data["text"]

    if "subtopics" in topic_dict:
        for sub_key, sub_val in topic_dict["subtopics"].items():
            if sub_key == subtopic_name:
                return sub_val.get("text")
            found = find_subtopic_text(sub_val, subtopic_name)
            if found:
                return found

    for key, value in topic_dict.items():
        if isinstance(value, dict):
            found = find_subtopic_text(value, subtopic_name)
            if found:
                return found

    return None


def load_json_safe_from_base(filename):
    file_path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(file_path):
        print(f"File not found: {filename} — using empty fallback.")
        return {}
    with open(file_path, 'r') as f:
        return json.load(f)


def load_json_safe_from_subject(subject, filename):
    subject_dir = os.path.join(DATA_DIR, subject.lower())
    file_path = os.path.join(subject_dir, filename)
    if not os.path.exists(file_path):
        print(f"File not found: {subject}/{filename} — using empty fallback.")
        return {}
    with open(file_path, 'r') as f:
        return json.load(f)


def load_config():
    file_path = os.path.join(BASE_DIR, "config.json")
    if not os.path.exists(file_path):
        raise FileNotFoundError("config.json not found. Please create it with 'model' and 'api_key'.")
    with open(file_path, 'r') as f:
        return json.load(f)


# --------------- Prompt Builder ---------------

def build_prompt(params, textbook_data, curriculum_data, examples_data, rubric_data):
    subject = params.get('subject', 'Unknown Subject')
    grade_level = params.get('grade_level', 'Unknown Grade')
    topic = params.get('topic', 'Unknown Topic')
    subtopic = params.get('subtopic', 'Unknown Subtopic')
    bloom_level = params.get('bloom_level', 'Understand')
    num_questions = params.get('num_questions', 5)
    user_keywords = params.get('user_keywords', '')

    textbook_content = find_subtopic_text(textbook_data, subtopic) or "Use general knowledge about the subtopic."
    curriculum_content = curriculum_data.get(subtopic) or "Use standard curriculum expectations for this topic and grade."
    example_qas = examples_data.get(subtopic) or []
    rubric_structure = rubric_data if rubric_data else {
        "criteria": "Use standard marking criteria appropriate for grade level and Bloom's Taxonomy level."
    }

    prompt = f"""
You are an expert educational content generator.
Create high-quality Q&As and rubrics for the following:

Subject: {subject}
Grade Level: {grade_level}
Topic: {topic}
Subtopic: {subtopic}
Bloom’s Taxonomy Level: {bloom_level}
Number of Questions: {num_questions}
User Keywords: {user_keywords}

Context:
- Textbook: {textbook_content}
- Curriculum: {curriculum_content}
- Example Q&As: {example_qas}
- Rubric Structure: {rubric_structure}

 Output the result in valid JSON using this structure:
{{
  "Q&A&rubrics": [
    {{
      "question": "string",
      "answer": "string",
      "rubric": "string"
    }}
  ]
}}
"""
    return prompt


# --------------- API Calls ---------------

def call_openai_api(prompt, api_key, model_name):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return {"choices": [{"message": {"content": response.choices[0].message.content}}]}


def call_mistral_api(prompt, api_key):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "mistral-medium-latest",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def call_llm_api(prompt, config):
    model_name = config.get("model", "").lower()
    api_key = config.get("api_key")

    if not api_key:
        raise ValueError("API key not found in config.json")

    if "mistral" in model_name:
        return call_mistral_api(prompt, api_key)
    elif "gpt" in model_name:
        return call_openai_api(prompt, api_key, model_name)
    else:
        raise ValueError(f"Unsupported model: {model_name}")


# --------------- Parse & Save ---------------

def parse_and_save_response(response_json, output_file):
    message = response_json['choices'][0]['message']['content']

    if "```json" in message:
        message = message.split("```json")[1].split("```")[0].strip()
    elif "```" in message:
        message = message.split("```")[1].strip()

    try:
        data = json.loads(message)
    except json.JSONDecodeError as e:
        print(f"  Failed to parse LLM output: {e}")
        raise

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f" Q&As and rubrics saved to {output_file}")


# --------------- Main ---------------

def main():
    params = load_json_safe_from_base('parameters.json')
    subject = params.get('subject', 'general').lower()

    textbook_data = load_json_safe_from_subject(subject, 'book.json')
    curriculum_data = load_json_safe_from_subject(subject, 'curriculum.json')
    examples_data = load_json_safe_from_subject(subject, 'examples.json')
    rubric_data = load_json_safe_from_subject(subject, 'rubrics.json')

    prompt = build_prompt(params, textbook_data, curriculum_data, examples_data, rubric_data)

    config = load_config()

    response = call_llm_api(prompt, config)

    output_folder = params.get('output_folder', 'results')
    output_folder_path = os.path.join(BASE_DIR, output_folder)
    os.makedirs(output_folder_path, exist_ok=True)

    output_file = os.path.join(output_folder_path, 'output.json')
    parse_and_save_response(response, output_file)


if __name__ == "__main__":
    main()
