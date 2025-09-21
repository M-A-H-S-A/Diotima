import os
import json
import time
import datetime
import csv
import re

# Assuming all your helper files are in a 'src' directory relative to main.py
from src.config_loader import load_config
from src.data_loader import (
    load_json_safe_from_base,
    load_json_safe_from_subject,
    find_subtopic_text,
    find_focused_context,
    get_verbs_for_bloom_level
)
from src.prompt_builder import build_questions_prompt, build_AnswerRubrics_prompt
from src.llm_api_client import call_llm_api
from src.output_processor import (
    parse_questions_response,
    parse_qna_response,
    save_questions_with_content
)

# Global BASE_DIR for easy path management
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def log_token_usage(model, prompt_tokens, completion_tokens, total_tokens, duration_sec, params_data, log_file):
    """Logs a single line for a completed API call."""
    param_fields_to_log = [
        'subject',
        'grade_level',
        'topic',
        'subtopic',
        'bloom_level',
        'num_questions',
        'user_keywords'
    ]
    data_row = {
        "timestamp": datetime.datetime.now(),
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "duration_sec": f"{duration_sec:.2f}"
    }
    for field in param_fields_to_log:
        value = params_data.get(field)
        if field == 'bloom_level' and isinstance(value, list):
            data_row[field] = ", ".join(value)
        else:
            data_row[field] = value if value is not None else ""

    log_path = os.path.join(BASE_DIR, log_file)
    is_first_time = not os.path.exists(log_path)
    fieldnames = list(data_row.keys())

    with open(log_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if is_first_time:
            writer.writeheader()
        writer.writerow(data_row)


def main():
    print("Starting content generation process with prompt chaining...")

    # Load parameters and configuration
    params = load_json_safe_from_base('parameters.json')
    config = load_config()

    # Subject and Bloom levels
    subject = params.get('subject', 'biology').lower()
    bloom_levels_raw = params.get('bloom_level', 'Analyzing, Evaluating')
    bloom_levels = [b.strip() for b in bloom_levels_raw.split(',') if b.strip()]

    # Load verbs per Bloom level for this subject
    glossary_verbs = {level: get_verbs_for_bloom_level(level, subject) for level in bloom_levels}

    # Output folder setup
    custom_output_folder = params.get('output_folder', 'default')
    subject_dir = os.path.join(DATA_DIR, subject)
    output_folder_path = os.path.join(subject_dir, 'results', custom_output_folder)
    os.makedirs(output_folder_path, exist_ok=True)
    log_file_path = os.path.join(output_folder_path, 'token_log.csv')
    print(f"Subject: {subject}, Output Folder: {output_folder_path}")

    # Load data files
    print("Loading data files...")
    textbook_data = load_json_safe_from_subject(subject, 'book.json')
    curriculum_data = load_json_safe_from_subject(subject, 'curriculum.json')
    examples_data = load_json_safe_from_subject(subject, 'examples.json')
    rubric_structure = load_json_safe_from_subject(subject, 'rubrics.json')
    print("Data files loaded.")

    # =========================
    # Step 1: Generate Questions
    # =========================
    print("Step 1: Generating questions...")
    questions_prompt = build_questions_prompt(
        params, textbook_data, curriculum_data, examples_data, glossary_verbs
    )

    try:
        response_questions, tokens_q, duration_q = call_llm_api(questions_prompt, config, params)
        log_token_usage(config['model'], *tokens_q, duration_q, params, log_file_path)
        questions_by_bloom = parse_questions_response(response_questions)

        # Save questions with their source text
        questions_file_with_content = os.path.join(output_folder_path, 'questions_with_content.json')
        save_questions_with_content(questions_by_bloom, questions_file_with_content)
        print(f"Questions with source content saved to {questions_file_with_content}")

    except Exception as e:
        print(f"An error occurred during question generation: {e}")
        return

    total_questions = sum(len(q_list) for q_list in questions_by_bloom.values())
    print(f"Generated a total of {total_questions} questions across all Bloom levels.")

    # =========================
    # Step 2: Generate Q&A per question
    # =========================
    final_output_grouped = {}
    subtopic = params.get('subtopic', 'Unknown Subtopic')

    full_subtopic_text = find_subtopic_text(textbook_data, subtopic) or ""
    if not full_subtopic_text:
        print(f"Warning: Could not find content for subtopic '{subtopic}'. Using general knowledge.")

    for bloom_level, questions_list_objects in questions_by_bloom.items():
        print(f"\nProcessing questions for Bloom's level: {bloom_level}...")
        qna_for_level = []
        for i, q_obj in enumerate(questions_list_objects):
            question = q_obj.get('question', '')
            if not question:
                print(f"Skipping malformed question object: {q_obj}")
                continue

            print(f"  > Generating Q&A for question {i + 1}/{len(questions_list_objects)}...")
            focused_context = find_focused_context(question, full_subtopic_text)
            qna_prompt = build_AnswerRubrics_prompt(question, bloom_level, focused_context, rubric_structure)

            try:
                response_qna, tokens_qa, duration_qa = call_llm_api(qna_prompt, config, params)
                log_token_usage(config['model'], *tokens_qa, duration_qa, params, log_file_path)
                qna_pair = parse_qna_response(response_qna)
                qna_pair['source_text'] = q_obj.get('source_text', 'N/A')
                qna_for_level.append(qna_pair)

            except Exception as e:
                print(f"An error occurred for question '{question[:30]}...': {e}. Skipping.")
                continue

        final_output_grouped[bloom_level] = qna_for_level

    print("\nAll Q&As and rubrics generated.")

    # =========================
    # Step 3: Save final output
    # =========================
    final_output = {"Output": final_output_grouped}
    output_file = os.path.join(output_folder_path, 'output.json')

    with open(output_file, 'w') as f:
        json.dump(final_output, f, indent=2)

    print(f"Process completed successfully. Final output saved to {output_file}")


if __name__ == "__main__":
    main()
