import os
import json

# BASE_DIR for data_loader.py is its own directory (src/)
# To get to the project root (where parameters.json and data/ are), we go up one level.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) # This is src/
PROJECT_ROOT = os.path.dirname(PROJECT_ROOT) # Now this is edu_content_generator/

DATA_DIR = os.path.join(PROJECT_ROOT, "data") # Data folder is relative to project root

def load_json_safe_from_base(filename):
    """Loads a JSON file from the project root directory."""
    file_path = os.path.join(PROJECT_ROOT, filename) # Use PROJECT_ROOT here
    if not os.path.exists(file_path):
        print(f"File not found: {filename} — using empty fallback.")
        return {}
    with open(file_path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in {filename}: {e}")
            print(f"Please ensure {filename} is valid JSON and does NOT contain comments.")
            raise

def load_json_safe_from_subject(subject, filename):
    """Loads a JSON file from a subject-specific data directory."""
    subject_dir = os.path.join(DATA_DIR, subject.lower())
    file_path = os.path.join(subject_dir, filename)
    if not os.path.exists(file_path):
        print(f"File not found: {subject}/{filename} — using empty fallback.")
        return {}
    with open(file_path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in {subject}/{filename}: {e}")
            raise

def find_subtopic_text(structured_book, subtopic_name):
    """
    Search for the subtopic_name in the structured_book and return its text content.
    """
    for topic, subtopics in structured_book.items():
        if subtopic_name in subtopics:
            return subtopics[subtopic_name]
    print(f"Warning: Subtopic '{subtopic_name}' not found in references.")
    return None

def find_topic_text(structured_book, topic_name):
    """
    Search for the topic_name in the structured_book and return its text content.
    """
    if topic_name in structured_book:
        return structured_book[topic_name]
    print(f"Warning: Topic '{topic_name}' not found in the references.")
    return None

if __name__ == '__main__':
    # Example usage:
    print("Loading parameters.json...")
    # For standalone testing of data_loader, we need to ensure parameters.json exists
    # or mock it. Let's create a temporary one.
    temp_params_path = os.path.join(PROJECT_ROOT, 'parameters.json')
    with open(temp_params_path, 'w') as f:
        json.dump({"subject": "test_subject", "topic": "Test Topic"}, f)

    params = load_json_safe_from_base('parameters.json')
    print(f"Loaded params: {params.get('subject')}, {params.get('topic')}")

    subject_example = params.get('subject', 'biology').lower()
    print(f"\nLoading data for subject: {subject_example}...")

    # Create temporary subject data for testing
    test_subject_dir = os.path.join(DATA_DIR, subject_example)
    os.makedirs(test_subject_dir, exist_ok=True)
    with open(os.path.join(test_subject_dir, 'book.json'), 'w') as f:
        json.dump({"Test Topic": {"Test Subtopic": "Some test content."}}, f)
    with open(os.path.join(test_subject_dir, 'curriculum.json'), 'w') as f:
        json.dump({"Test Topic": "Curriculum for test topic."}, f)

    book_data = load_json_safe_from_subject(subject_example, 'book.json')
    curriculum_data = load_json_safe_from_subject(subject_example, 'curriculum.json')
    print(f"Book content for 'Test Subtopic': {find_subtopic_text(book_data, 'Test Subtopic')[:50]}...")

    # Clean up test files
    os.remove(temp_params_path)
    os.remove(os.path.join(test_subject_dir, 'book.json'))
    os.remove(os.path.join(test_subject_dir, 'curriculum.json'))
    os.rmdir(test_subject_dir)