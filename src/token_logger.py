# Logs token usage and timestamps

import datetime
import csv
import os

# BASE_DIR is defined relative to this file's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def log_token_usage(model, prompt_tokens, completion_tokens, total_tokens, duration_sec, params_data, log_file=None):
    """
    Logs token usage and generation parameters to a CSV file.
    """
    log_file = log_file or "token_log.csv"
    # Ensure log_path is relative to the project root if BASE_DIR is project root
    # If BASE_DIR is the module's directory, adjust log_path to go up to project root
    # For simplicity, assuming log_file can be directly in BASE_DIR for this module's test
    # In main.py, log_file_path is constructed relative to the output folder.
    log_path = os.path.join(BASE_DIR, log_file)

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
        "timestamp": datetime.datetime.now().isoformat(), # Use ISO format for better sorting/parsing
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

    is_first_time = not os.path.exists(log_path)
    fieldnames = list(data_row.keys())

    with open(log_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if is_first_time:
            writer.writeheader()
        writer.writerow(data_row)
    # print(f"Logged token usage to {log_path}") # Optional: for debugging

if __name__ == '__main__':
    # Example usage:
    mock_params = {
        'subject': 'Test Subject',
        'grade_level': 'Test Grade',
        'topic': 'Test Topic',
        'subtopic': 'Test Subtopic',
        'bloom_level': ['Remembering', 'Creating'],
        'num_questions': 3,
        'user_keywords': 'keyword1, keyword2'
    }
    test_log_file = "test_token_log.csv"
    log_token_usage("test-model", 100, 200, 300, 5.23, mock_params, log_file=test_log_file)
    print(f"Check '{test_log_file}' for test log entry.")
    # You might want to remove the test file afterwards for clean runs
    # os.remove(os.path.join(BASE_DIR, test_log_file))