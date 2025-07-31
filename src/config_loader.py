import os
import json


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) # This is src/
PROJECT_ROOT = os.path.dirname(PROJECT_ROOT) # Now this is edu_content_generator/

def load_config():
    """
    Loads configuration from config.json and environment variables.
    Prioritizes environment variables for API keys.
    """
    mistral_api_key_env = os.getenv("MISTRAL_API_KEY")
    openai_api_key_env = os.getenv("OPENAI_API_KEY")
    gemini_api_key_env = os.getenv("GEMINI_API_KEY")

    config = {}
    # Use PROJECT_ROOT to find config.json
    file_path = os.path.join(PROJECT_ROOT, "config.json")

    config_from_file = {}
    if os.path.exists(file_path):
        cleaned_lines = []
        with open(file_path, 'r') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line.startswith('//') or stripped_line.startswith('#'):
                    continue
                if '//' in stripped_line:
                    stripped_line = stripped_line.split('//')[0]
                if '#' in stripped_line:
                    stripped_line = stripped_line.split('#')[0]
                cleaned_lines.append(stripped_line)

        cleaned_json_string = "\n".join(cleaned_lines)

        try:
            config_from_file = json.loads(cleaned_json_string)
            config['model'] = config_from_file.get('model')
        except json.JSONDecodeError as e:
            print(f"Error parsing config.json after comment stripping: {e}")
            print("Please ensure your config.json is valid JSON format *after* comments are removed.")
            print("Problematic content attempted to parse:\n", cleaned_json_string)
            raise

    model_choice = config.get('model', '').lower()
    chosen_api_key = None

    if "mistral" in model_choice:
        chosen_api_key = mistral_api_key_env or config_from_file.get('mistral_api_key')
        if not chosen_api_key:
            raise ValueError("Mistral API key not found. Please set MISTRAL_API_KEY environment variable or provide 'mistral_api_key' in config.json.")
    elif "gpt" in model_choice:
        chosen_api_key = openai_api_key_env or config_from_file.get('openai_api_key')
        if not chosen_api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable or provide 'openai_api_key' in config.json.")
    elif "gemini" in model_choice:
        chosen_api_key = gemini_api_key_env or config_from_file.get('gemini_api_key')
        if not chosen_api_key:
            raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY environment variable or provide 'gemini_api_key' in config.json.")
    elif "llama" in model_choice:
        chosen_api_key = None # No API key for local Ollama
    else:
        raise ValueError(f"Model '{config.get('model')}' not specified in config.json or unsupported model. Please choose from 'mistral-large-latest', 'gpt-4o', 'gemini-pro', or 'llama3' etc.")

    config['api_key'] = chosen_api_key
    return config

if __name__ == '__main__':
    try:
        cfg = load_config()
        print("Loaded Config:")
        print(f"  Model: {cfg.get('model')}")
        print(f"  API Key (masked): {cfg.get('api_key')[:5]}..." if cfg.get('api_key') else 'None')
    except ValueError as e:
        print(f"Error loading config: {e}")