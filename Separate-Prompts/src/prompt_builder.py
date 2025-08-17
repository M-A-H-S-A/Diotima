from .data_loader import find_subtopic_text, find_topic_text

def build_questions_prompt(params, textbook_data, curriculum_data, examples_data):
    """
    Constructs the prompt string for the LLM to generate questions, grouped by Bloom's level.
    """
    bloom_levels_raw = params.get('bloom_level', '')
    bloom_levels = [b.strip() for b in bloom_levels_raw.split(',') if b.strip()]
    num_questions = params.get('num_questions')

    subject = params.get('subject', 'Unknown Subject')
    grade_level = params.get('grade_level', 'Unknown Grade')
    topic = params.get('topic', 'Unknown Topic')
    subtopic = params.get('subtopic', 'Unknown Subtopic')
    user_keywords = params.get('user_keywords', '')

    textbook_content = find_subtopic_text(textbook_data, subtopic) or "Use general knowledge."
    curriculum_content = find_topic_text(curriculum_data, topic) or "Use curriculum expectations."
    example_qas = examples_data.get(subtopic) or []

    prompt = f"""
You are an expert curriculum designer.
Using the following context, generate exactly {num_questions} questions for EACH of the following Bloom's Taxonomy levels: {', '.join(bloom_levels)}.

Each question must:
- Be appropriate for Subject: {subject}, Grade: {grade_level}
- Focus on the Topic: {topic} and Subtopic: {subtopic}
- Draw from the provided context and examples.

Context:
- Textbook Content: {textbook_content}
- Curriculum Guidance: {curriculum_content}
- Example Q&As: {example_qas}
- User Keywords: {user_keywords}
For each question, you must also provide the exact text snippet from the provided context that was used to generate it. The source text must be a complete sentence or paragraph.

Format your output as a valid JSON object. Do not include any extra text or markdown.

{{
  "questions": {{
    "<BloomLevel1>": [
      "Question 1?",
      "Question 2?",
      ...
    ],
    "<BloomLevel2>": [
      ...
    ]
  }}
}}
"""
    return prompt.strip()

def build_qna_prompt(question, bloom_level, focused_context, rubric_data):
    """
    Constructs the prompt string for the LLM to generate an answer and rubric for a single question.
    It now includes a small, highly focused context.
    """
    prompt = f"""
You are an expert educator and grader.
Given the following question and Bloom's Taxonomy level, generate a detailed answer and a 3-level rubric.
The rubric should be aligned with the question's difficulty and the specified Bloom's Taxonomy level.

Question: {question}
Bloom's Taxonomy Level: {bloom_level}

Context:
- Textbook Content: {focused_context}
- Rubric Structure (with glossary verbs): {rubric_data}

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
        "level": "Competent Response",
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

Do not include any extra text or markdown.
"""
    return prompt.strip()