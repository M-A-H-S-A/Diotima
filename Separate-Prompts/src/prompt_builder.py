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

    # Keep JSON example outside the f-string to avoid brace escaping issues
    json_example = """
{
  "questions": {
    "<BloomLevel1>": [
      {
        "question": "What is the function of the cell membrane?",
        "source_text": "The cell membrane controls what enters and leaves the cell."
      },
      {
        "question": "Explain the role of enzymes in digestion.",
        "source_text": "Enzymes break down large molecules into smaller molecules that the body can absorb."
      }
    ],
    "<BloomLevel2>": [
      ...
    ]
  }
}
"""

    prompt = f"""
You are an expert curriculum designer.
Using the following context, generate exactly {num_questions} questions for EACH of the following Bloom's Taxonomy levels: {', '.join(bloom_levels)}.

Each question must:
- Be appropriate for Subject: {subject}, Grade: {grade_level}
- Focus on the Topic: {topic} and Subtopic: {subtopic}
- Be fully self-contained and **must never** mention or reference a textbook, passage, context, or guidance in the wording.
- Use the textbook/curriculum content internally to create the question, but keep that hidden from students.
- Always include the supporting "source_text" (the exact sentence/paragraph from the textbook or curriculum used).
- "source_text" must always be a single string (if multiple relevant points, join them with ' | ').
- If no supporting content is available, skip generating the question.
- Do NOT add explanations, examples, or reasoning outside the required fields.
- Ensure questions use clear, age-appropriate language for students under 18.

Context:
- Textbook Content: {textbook_content}
- Curriculum Guidance: {curriculum_content}
- Example Q&As: {example_qas}
- User Keywords: {user_keywords}

Format your output as a valid JSON object.
Each question must include:
- "question": the student-facing question (self-contained, no references to text/context)
- "source_text": the exact snippet from textbook/curriculum that supports it (hidden from students)

{json_example}
"""
    return prompt.strip()


def build_AnswersRubrics_prompt(question, bloom_level, focused_context, rubric_data):
    """
    Constructs the prompt string for the LLM to generate an answer and rubric for a single question.
    The answer must ONLY use the provided focused_context.
    """

    # Example rubric JSON structure as a static string
    rubric_example = """
{
  "question": "Sample question here",
  "answer": "...",
  "rubric": {
    "levels": [
      {
        "level": "Comprehensive Response",
        "description": "..."
      },
      {
        "level": "Competent Response",
        "description": "..."
      },
      {
        "level": "Partial Response",
        "description": "..."
      },
      {
        "level": "Limited Response",
        "description": "..."
      }
    ]
  }
}
"""

    prompt = f"""
You are an expert educator and grader.
Given the following question and Bloom's Taxonomy level, generate a detailed answer and a 4-level rubric.
The answer must be based **only on the provided context** (do not invent information outside it).
The rubric should be aligned with the question's difficulty and the specified Bloom's Taxonomy level.
Answer and rubric must not be too complex.
Do NOT add explanations, examples, or extra reasoning beyond what is requested. Only provide the JSON fields exactly as specified.
- Make sure the answer and rubric are written in age-appropriate language for students under 18.
- The rubric must be objective, transparent, and aligned with Bloom’s verbs.
- Do not include subjective, biased, or culturally sensitive assumptions.

Question: {question}
Bloom's Taxonomy Level: {bloom_level}

Context:
- Textbook Content: {focused_context}
- Rubric Structure (with glossary verbs): {rubric_data}

Format your output as valid JSON using the structure below:

{rubric_example}

Do not include any extra text or markdown.
"""
    return prompt.strip()
