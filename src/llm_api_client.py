
import requests
import os
import time
from openai import OpenAI
import google.generativeai as genai
import ollama
import anthropic

# Relative import assumes this file is part of a package
from .token_logger import log_token_usage

def call_mistral_api(prompt, api_key, params_data, log_file=None):
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
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Mistral API call failed: {e}")
        raise # Re-raise for main to handle

    duration = time.time() - start_time
    result = response.json()

    usage = result.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", 0)

    if log_file:
        log_token_usage("mistral-large-latest", prompt_tokens, completion_tokens, total_tokens, duration, params_data, log_file)

    return result

def call_openai_api(prompt, api_key, model_name, params_data, log_file=None):
    client = OpenAI(api_key=api_key)
    start_time = time.time()

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    try:
        if model_name.startswith("o"):  # newer models like o3-mini
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_completion_tokens=4000
            )
        else:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=4000
            )
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        raise

    duration = time.time() - start_time
    usage = response.usage

    log_token_usage(
        model_name,
        usage.prompt_tokens,
        usage.completion_tokens,
        usage.total_tokens,
        duration,
        params_data,
        log_file
    )

    return {"choices": [{"message": {"content": response.choices[0].message.content}}]}

def call_gemini_api(prompt, api_key, model_name, params_data, log_file=None):
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

        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            prompt_tokens = usage.prompt_token_count if hasattr(usage, 'prompt_token_count') else 0
            completion_tokens = usage.candidates_token_count if hasattr(usage, 'candidates_token_count') else 0
            total_tokens = usage.total_token_count if hasattr(usage, 'total_token_count') else 0
        else:
            print("Warning: Gemini usage_metadata not directly available in response. Token counts might be estimated or 0.")


        if log_file:
            log_token_usage(model_name, prompt_tokens, completion_tokens, total_tokens, duration, params_data, log_file)

        return {"choices": [{"message": {"content": message}}]}

    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
            print(f"Gemini API call blocked: {response.prompt_feedback.block_reason}")
        raise

def call_llama_api(prompt, model_name, ollama_host, params_data, log_file=None):
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
    except Exception as e: # Catch broader exceptions from Ollama client
        print(f"Ollama API call failed: {e}")
        raise

    duration = time.time() - start_time

    prompt_tokens = response.get('prompt_eval_count', 0)
    completion_tokens = response.get('eval_count', 0)
    total_tokens = prompt_tokens + completion_tokens

    generated_content = response['message']['content']

    if log_file:
        log_token_usage(model_name, prompt_tokens, completion_tokens, total_tokens, duration, params_data, log_file)

    return {"choices": [{"message": {"content": generated_content}}]}


def call_claude_api(prompt, api_key, model_name, params_data, log_file=None):
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

    if log_file:
        log_token_usage(model_name, prompt_tokens, completion_tokens, total_tokens, duration, params_data, log_file)

    return {"choices": [{"message": {"content": content}}]}


def call_llm_api(prompt, config, params_data, log_file=None):
    model_name = config.get("model", "").lower()
    api_key = config.get("api_key")

    if "claude" in model_name:
        return call_claude_api(prompt, api_key, model_name, params_data, log_file=log_file)
    elif "mistral" in model_name:
        return call_mistral_api(prompt, api_key, params_data, log_file=log_file)
    elif "gpt" in model_name or model_name.startswith("o"):
        return call_openai_api(prompt, api_key, model_name, params_data, log_file=log_file)
    elif "gemini" in model_name:
        if not model_name.startswith("models/"):
            model_name = "models/" + model_name
        return call_gemini_api(prompt, api_key, model_name, params_data, log_file=log_file)
    elif "llama" in model_name:
        ollama_host = config.get("ollama_host", "http://localhost:11434")
        return call_llama_api(prompt, model_name, ollama_host, params_data, log_file=log_file)
    else:
        raise ValueError(f"Unsupported model: {model_name}")

if __name__ == '__main__':
    # This section for testing requires a valid config and possibly mocked responses.
    # It's generally harder to test API calls in isolation without mocks or actual keys.
    print("This module contains API client functions. Run main.py to use them.")
