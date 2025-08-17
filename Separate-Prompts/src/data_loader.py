# In src/data_loader.py
import os
import json
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')


def load_json_safe_from_base(filename):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {filename}")
    with open(file_path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error parsing JSON in {filename}: {e}", e.doc, e.pos)


def load_json_safe_from_subject(subject, filename):
    subject_dir = os.path.join(DATA_DIR, subject.lower())
    file_path = os.path.join(subject_dir, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {subject}/{filename}")
    with open(file_path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error parsing JSON in {subject}/{filename}: {e}", e.doc, e.pos)


def find_subtopic_text(structured_book, subtopic_name):
    for topic_data in structured_book.values():
        if isinstance(topic_data, dict) and subtopic_name in topic_data:
            return topic_data[subtopic_name]
    return None


def find_topic_text(structured_curriculum, topic_name):
    if topic_name in structured_curriculum:
        return structured_curriculum[topic_name]
    return None


def find_focused_context(question, full_subtopic_text, num_sentences=5):
    """
    Finds the most relevant sentences in a block of text based on keywords in the question.
    Returns a short, focused context.
    """
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', full_subtopic_text)
    keywords = set(re.findall(r'\b\w+\b', question.lower()))

    relevant_sentences = []

    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in keywords):
            relevant_sentences.append(sentence)

    if not relevant_sentences:
        return ' '.join(sentences[:num_sentences])

    return ' '.join(relevant_sentences[:num_sentences])