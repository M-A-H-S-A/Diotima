import os
from src.config_loader import load_config
from src.data_loader import load_json_safe_from_base, load_json_safe_from_subject, DATA_DIR
from src.prompt_builder import build_prompt
from src.llm_api_client import call_llm_api
from src.output_processor import parse_and_save_response


# token_logger is imported within llm_api_client implicitly, no direct import needed here

def main():
    print("Starting content generation process...")

    # 1. Load parameters and config
    params = load_json_safe_from_base('parameters.json')
    config = load_config()

    subject = params.get('subject', 'general').lower()
    custom_output_folder = params.get('output_folder', 'default')

    # Create output directory
    subject_dir = os.path.join(DATA_DIR, subject)  # DATA_DIR from data_loader
    output_folder_path = os.path.join(subject_dir, 'results', custom_output_folder)
    os.makedirs(output_folder_path, exist_ok=True)
    log_file_path = os.path.join(output_folder_path, 'token_log.csv')

    print(f"Subject: {subject}, Output Folder: {output_folder_path}")

    # 2. Load all data sources
    print("Loading data files...")
    textbook_data = load_json_safe_from_subject(subject, 'book.json')
    curriculum_data = load_json_safe_from_subject(subject, 'curriculum.json')
    examples_data = load_json_safe_from_subject(subject, 'examples.json')
    rubric_data = load_json_safe_from_subject(subject, 'rubrics.json')
    print("Data files loaded.")

    # 3. Build the prompt
    print("Building prompt for the LLM...")
    prompt = build_prompt(params, textbook_data, curriculum_data, examples_data, rubric_data)
    # print(f"Generated prompt (first 500 chars):\n{prompt[:500]}...") # For debugging

    # 4. Call the LLM API
    print(f"Calling LLM: {config.get('model')}...")
    try:
        response = call_llm_api(prompt, config, params, log_file=log_file_path)
        print("LLM call successful.")
    except Exception as e:
        print(f"An error occurred during the LLM API call: {e}")
        return  # Exit if API call fails

    # 5. Parse and save the response
    output_file = os.path.join(output_folder_path, 'output.json')
    try:
        parse_and_save_response(response, output_file)
        print(f"Process completed successfully. Output saved to {output_file}")
    except Exception as e:
        print(f"An error occurred during parsing and saving the response: {e}")


if __name__ == "__main__":
    main()
# Entry point script
