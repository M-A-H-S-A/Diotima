import json
import requests
import os
import time
from openai import OpenAI


# Time and Token

import datetime

def log_token_usage(model, prompt_tokens, completion_tokens, total_tokens, duration_sec, log_file=None):
    log_file = log_file or "token_log.csv"
    log_path = os.path.join(BASE_DIR, log_file)

    is_first_time = not os.path.exists(log_path)

    with open(log_path, 'a') as f:
        if is_first_time:
            f.write("timestamp,model,prompt_tokens,completion_tokens,total_tokens,duration_sec\n")
        f.write(f"{datetime.datetime.now()},{model},{prompt_tokens},{completion_tokens},{total_tokens},{duration_sec:.2f}\n")


# Always get base dir of this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")  # /data root

# --------------- Helpers ---------------

def find_subtopic_text(structured_book, subtopic_name):
    """
    Search for the subtopic_name in the structured_book and return its text content.
    """
    for topic, subtopics in structured_book.items():
        if subtopic_name in subtopics:
            return subtopics[subtopic_name]
    print(f"Warning: Subtopic '{subtopic_name}' not found in refrences.")
    return None

def find_topic_text(structured_book, topic_name):
    """
    Search for the topic_name in the structured_book and return its text content.
    """
    if topic_name in structured_book:
        return structured_book[topic_name]
    print(f"Warning: Topic '{topic_name}' not found in the references.")
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
    # Sanitize Bloom levels
    bloom_levels_raw = params.get('bloom_level', '')
    bloom_levels = [b.strip() for b in bloom_levels_raw.split(',') if b.strip()]
    params['bloom_level'] = bloom_levels  # Overwrite with cleaned list

    subject = params.get('subject', 'Unknown Subject')
    grade_level = params.get('grade_level', 'Unknown Grade')
    topic = params.get('topic', 'Unknown Topic')
    subtopic = params.get('subtopic', 'Unknown Subtopic')
    bloom_levels = params.get('bloom_level', [])  # Already sanitized to a list
    num_questions = params.get('num_questions')
    user_keywords = params.get('user_keywords', '')

    textbook_content = find_subtopic_text(textbook_data, subtopic) or "Use general knowledge."
    curriculum_content = find_topic_text(curriculum_data, topic) or "Use curriculum expectations."
    example_qas = examples_data.get(subtopic) or []

    prompt = f"""
You are a skilled educational content designer.

Using the textbook, curriculum, and examples provided, generate Q&A pairs with rubrics for each of the following Bloom's Taxonomy levels: {', '.join(bloom_levels)}.
Each Bloom level should have exactly {num_questions} questions generated.

Each Q&A must:
- Be appropriate for Subject: {subject}, Grade: {grade_level}
- Focus on the Topic: {topic} and Subtopic: {subtopic}
- Use verbs from the rubric structure for each Bloom level
- Include a rubric aligned with the question's Bloom level and verb used

Context of Q&A must:
- Textbook Content: {textbook_content}
- Curriculum Guidance: {curriculum_content}
- Example Q&As: {example_qas}
- Rubric Structure (with glossary verbs): {rubric_data}
- User Keywords: {user_keywords}

Format your output as valid JSON:

{{
  "Output": {{
    "<BloomLevel>": [
      {{
        "question": "Explain why viruses are difficult to classify as living organisms.",
        "answer": "...",
        "rubric": {{
          "levels": [
            {{
              "level": "Comprehensive Response",
              "description": "..."
            }},
            {{
              "level": "Partial Response",
              "description": "..."
            }},
            {{
              "level": "Limited Response",
              "description": "..."
            }}
          ]
        }}
      }}
    ],
    "Applying": [
      ...
    ]
  }}
}}

Only include Bloom levels from this list: {bloom_levels}
Generate a balanced set of questions by Bloom’s level. You must include questions for each Bloom’s Taxonomy Levels: {", ".join(bloom_levels)}
Do not include any Bloom level not mentioned.
Skip any other levels.
If rubric is not applicable, return `"rubric": null`.
IMPORTANT: ONLY return the valid JSON object described above. No extra text or markdown.

"""
    return prompt.strip()


# --------------- API Calls ---------------

import time

def call_mistral_api(prompt, api_key, log_file=None):
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
        ],
        "max_tokens": 2000,
        "temperature": 0.7,
    }

    start_time = time.time()
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    duration = time.time() - start_time

    result = response.json()

    # Example: If Mistral returns token usage info like this:
    # tokens_used = result.get("usage", {}).get("total_tokens", None)
    # For now, assume no token info, so set to None or 0
    prompt_tokens = None
    completion_tokens = None
    total_tokens = None

    # Log if possible
    if log_file:
        # Use "mistral-medium-latest" as model name for logging
        log_token_usage(
            model="mistral-medium-latest",
            prompt_tokens=prompt_tokens or 0,
            completion_tokens=completion_tokens or 0,
            total_tokens=total_tokens or 0,
            duration_sec=duration,
            log_file=log_file
        )

    return result



def call_openai_api(prompt, api_key, model_name, log_file=None):
    client = OpenAI(api_key=api_key)
    start_time = time.time()
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    duration = time.time() - start_time
    usage = response.usage

    print(f"🔢 OpenAI Token Usage:")
    print(f"  Prompt tokens:     {usage.prompt_tokens}")
    print(f"  Completion tokens: {usage.completion_tokens}")
    print(f"  Total tokens:      {usage.total_tokens}")
    print(f"⏱️ Duration: {duration:.2f} seconds")

    # Save log
    log_token_usage(model_name, usage.prompt_tokens, usage.completion_tokens, usage.total_tokens, duration, log_file)

    return {"choices": [{"message": {"content": response.choices[0].message.content}}]}


def call_llm_api(prompt, config, log_file=None):
    model_name = config.get("model", "").lower()
    api_key = config.get("api_key")

    if not api_key:
        raise ValueError("API key not found in config.json")

    if "mistral" in model_name:
        return call_mistral_api(prompt, api_key, log_file=log_file)
    elif "gpt" in model_name:
        return call_openai_api(prompt, api_key, model_name, log_file=log_file)
    else:
        raise ValueError(f"Unsupported model: {model_name}")

# --------------- Parse & Save ---------------

def parse_and_save_response(response_json, output_file):
    message = response_json['choices'][0]['message']['content']
    #print("Raw model output:\n", message[:2000])  # print first 2000 chars for inspection

    # existing markdown stripping
    if "```json" in message:
        message = message.split("```json")[1].split("```")[0].strip()
    elif "```" in message:
        message = message.split("```")[1].strip()

    try:
        data = json.loads(message)
    except json.JSONDecodeError as e:
        print(f"⚠️  Failed to parse LLM output: {e}")
        raise

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ Q&As and rubrics saved to {output_file}")


# --------------- Main ---------------

def main():
    params = load_json_safe_from_base('parameters.json')
    subject = params.get('subject', 'general').lower()
    custom_output_folder = params.get('output_folder', 'default')

    subject_dir = os.path.join(DATA_DIR, subject)
    output_folder_path = os.path.join(subject_dir, 'results', custom_output_folder)
    os.makedirs(output_folder_path, exist_ok=True)

    log_file = os.path.join(output_folder_path, 'token_log.csv')

    textbook_data = load_json_safe_from_subject(subject, 'book.json')
    curriculum_data = load_json_safe_from_subject(subject, 'curriculum.json')
    examples_data = load_json_safe_from_subject(subject, 'examples.json')
    rubric_data = load_json_safe_from_subject(subject, 'rubrics.json')

    prompt = build_prompt(params, textbook_data, curriculum_data, examples_data, rubric_data)
    config = load_config()

    response = call_llm_api(prompt, config, log_file=log_file)
#    print("=== PROMPT ===")
#    print(prompt[:1500])  # print first 1500 chars to check what the model will see
#    print("==============")

    output_file = os.path.join(output_folder_path, 'output.json')
    parse_and_save_response(response, output_file)
if __name__ == "__main__":
    main()
