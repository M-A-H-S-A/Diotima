from .data_loader import find_subtopic_text, find_topic_text

def build_prompt(params, textbook_data, curriculum_data, examples_data, rubric_data):
    """
    Constructs the detailed prompt string for the LLM based on provided parameters and data.
    """
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
  "question": "{question}",
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

Only include Bloom levels from this list: {bloom_levels}
Generate a balanced set of questions by Bloom’s level. You must include questions for each Bloom’s Taxonomy Levels: {", ".join(bloom_levels)}
Do not include any Bloom level not mentioned.
Skip any other levels.
If rubric is not applicable, return `"rubric": null`.
IMPORTANT: ONLY return the valid JSON object described above. No extra text or markdown.

"""
    return prompt.strip()

if __name__ == '__main__':
    # Example usage:
    # This part would typically be run from main.py, but for testing,
    # you'd mock data or load it here.
    # For a simple test, let's create mock data:
    mock_params = {
        'subject': 'Biology',
        'grade_level': '10',
        'topic': 'Cells',
        'subtopic': 'Cell Organelles',
        'bloom_level': 'Understanding, Analyzing',
        'num_questions': 2,
        'user_keywords': 'mitochondria, nucleus'
    }
    mock_textbook = {'Cells': {'Cell Organelles': 'Mitochondria are the powerhouse...'}}
    mock_curriculum = {'Cells': 'Students will understand cell structure...'}
    mock_examples = {'Cell Organelles': [{'q': 'What is cytoplasm?', 'a': 'The jelly-like substance...'}]}
    mock_rubrics = {'Understanding': 'Define, Describe', 'Analyzing': 'Compare, Contrast'}

    print("Building prompt...")
    test_prompt = build_prompt(mock_params, mock_textbook, mock_curriculum, mock_examples, mock_rubrics)
    #print(test_prompt[:500] + "...") # Print first 500 chars
