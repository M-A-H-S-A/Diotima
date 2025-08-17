import os
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_config():
    """
    Load model config and determine the correct API key based on provider prefix.
    """
    # Load environment variables
    mistral_api_key_env = os.getenv("MISTRAL_API_KEY")
    openai_api_key_env = os.getenv("OPENAI_API_KEY")
    gemini_api_key_env = os.getenv("GEMINI_API_KEY")
    claude_api_key_env = os.getenv("ANTHROPIC_API_KEY")

    config = {}
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
            print("Problematic content:\n", cleaned_json_string)
            raise

    model_name = config.get('model', config_from_file.get('model', '')).lower()

    # Determine provider from model prefix
    if model_name.startswith("mistral"):
        provider = "mistral"
        api_key = mistral_api_key_env or config_from_file.get('mistral_api_key')
    elif model_name.startswith("gpt") or model_name.startswith("o") or model_name.startswith("text-") or model_name.startswith("davinci"):
        provider = "openai"
        api_key = openai_api_key_env or config_from_file.get('openai_api_key')
    elif model_name.startswith("models/gemini"):
        provider = "gemini"
        api_key = gemini_api_key_env or config_from_file.get('gemini_api_key')
    elif model_name.startswith("claude"):
        provider = "claude"
        api_key = claude_api_key_env or config_from_file.get('claude_api_key')
    elif model_name.startswith("llama"):
        provider = "llama"
        api_key = None
    else:
        raise ValueError(f"Unsupported or missing model: '{model_name}'.\nExpected prefixes: 'gpt', 'mistral', 'claude', 'gemini', 'llama'.")

    if provider != "llama" and not api_key:
        raise ValueError(f"{provider.title()} API key not found. Set it as an environment variable or in config.json.")

    config["model"] = model_name
    config["api_key"] = api_key
    config["provider"] = provider
    return config
if __name__ == '__main__':
    try:
        cfg = load_config()
        print("Loaded Config:")
        print(f"  Model: {cfg.get('model')}")
        print(f"  API Key (masked): {cfg.get('api_key')[:5]}..." if cfg.get('api_key') else 'None')
    except ValueError as e:
        print(f"Error loading config: {e}")