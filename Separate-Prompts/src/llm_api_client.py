import requests
import os
import time
from openai import OpenAI
import google.generativeai as genai
import ollama
import anthropic


def call_mistral_api(prompt, api_key, params_data):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "mistral-large-latest",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000,
        "temperature": 0.7,
    }

    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Mistral API call failed: {e}")
        raise

    duration = time.time() - start_time
    result = response.json()
    usage = result.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", 0)

    return result, (prompt_tokens, completion_tokens, total_tokens), duration


import time
from openai import OpenAI

def call_openai_api(prompt, api_key, model_name, params_data):
    """
    Calls the OpenAI chat completion API, automatically handling the
    parameter name change for new and future models.
    """
    client = OpenAI(api_key=api_key)
    start_time = time.time()
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    kwargs = {
        "model": model_name,
        "messages": messages
    }

    # Use a flexible check for newer models
    if any(m in model_name.lower() for m in ["gpt-4o", "gpt-5"]):
        kwargs["max_completion_tokens"] = params_data.get("max_tokens", 4000)
    else:
        kwargs["max_tokens"] = params_data.get("max_tokens", 4000)

    try:
        response = client.chat.completions.create(**kwargs)
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        raise

    duration = time.time() - start_time
    usage = response.usage

    return {"choices": [{"message": {"content": response.choices[0].message.content}}]}, \
           (usage.prompt_tokens, usage.completion_tokens, usage.total_tokens), duration
def call_gemini_api(prompt, api_key, model_name, params_data):
    genai.configure(api_key=api_key)
    if not model_name.startswith("models/"):
        model_name = "models/" + model_name
    model = genai.GenerativeModel(model_name)
    start_time = time.time()
    try:
        response = model.generate_content(
            contents=prompt,
            generation_config={
                "max_output_tokens": 65000,
                "temperature": 0.7,
                "response_mime_type": "application/json"
            }
        )
        duration = time.time() - start_time
        message = response.text
        usage = response.usage_metadata
        prompt_tokens = usage.prompt_token_count if hasattr(usage, 'prompt_token_count') else 0
        completion_tokens = usage.candidates_token_count if hasattr(usage, 'candidates_token_count') else 0
        total_tokens = usage.total_token_count if hasattr(usage, 'total_token_count') else 0
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
            print(f"Gemini API call blocked: {response.prompt_feedback.block_reason}")
        raise

    return {"choices": [{"message": {"content": message}}]}, \
        (prompt_tokens, completion_tokens, total_tokens), duration


def call_llama_api(prompt, model_name, ollama_host, params_data):
    client = ollama.Client(host=ollama_host)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    start_time = time.time()
    try:
        response = client.chat(
            model=model_name,
            messages=messages,
            options={
                "temperature": 0.7,
                "num_predict": 4000
            }
        )
    except Exception as e:
        print(f"Ollama API call failed: {e}")
        raise
    duration = time.time() - start_time
    prompt_tokens = response.get('prompt_eval_count', 0)
    completion_tokens = response.get('eval_count', 0)
    total_tokens = prompt_tokens + completion_tokens
    generated_content = response['message']['content']

    return {"choices": [{"message": {"content": generated_content}}]}, \
        (prompt_tokens, completion_tokens, total_tokens), duration


def call_claude_api(prompt, api_key, model_name, params_data):
    client = anthropic.Anthropic(api_key=api_key)
    messages = [
        {"role": "user", "content": prompt}
    ]
    start_time = time.time()
    try:
        response = client.messages.create(
            model=model_name,
            max_tokens=4000,
            temperature=0.7,
            system="You are a helpful assistant.",
            messages=messages
        )
    except Exception as e:
        print(f"Claude API call failed: {e}")
        raise

    duration = time.time() - start_time
    usage = response.usage
    prompt_tokens = usage.input_tokens
    completion_tokens = usage.output_tokens
    total_tokens = prompt_tokens + completion_tokens
    content = response.content[0].text if response.content else ""

    return {"choices": [{"message": {"content": content}}]}, \
        (prompt_tokens, completion_tokens, total_tokens), duration


def call_llm_api(prompt, config, params_data, log_file_path=None):
    model_name = config.get("model", "").lower()
    api_key = config.get("api_key")

    if "claude" in model_name:
        response, tokens, duration = call_claude_api(prompt, api_key, model_name, params_data)
    elif "mistral" in model_name:
        response, tokens, duration = call_mistral_api(prompt, api_key, params_data)
    elif "gpt" in model_name or model_name.startswith("o"):
        response, tokens, duration = call_openai_api(prompt, api_key, model_name, params_data)
    elif "gemini" in model_name:
        if not model_name.startswith("models/"):
            model_name = "models/" + model_name
        response, tokens, duration = call_gemini_api(prompt, api_key, model_name, params_data)
    elif "llama" in model_name:
        ollama_host = config.get("ollama_host", "http://localhost:11434")
        response, tokens, duration = call_llama_api(prompt, model_name, ollama_host, params_data)
    else:
        raise ValueError(f"Unsupported model: {model_name}")

    # Capture the formatted strings
    token_usage_str = f"🔢 {config.get('provider').capitalize()} Token Usage: Prompt={tokens[0]}, Completion={tokens[1]}, Total={tokens[2]}"
    duration_str = f"⏱️ Duration: {duration:.2f} seconds"

    # Print to console as a record
    print(token_usage_str)
    print(duration_str)

    # Write to log file if a path is provided
    if log_file_path:
        with open(log_file_path, 'a') as f:
            f.write(token_usage_str + '\n')
            f.write(duration_str + '\n')

    return response, tokens, duration