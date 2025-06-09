import os
import requests
import fitz  # PyMuPDF


# ------------- PDF Extraction Function -------------

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# ------------- Read Subtopics Function -------------

def read_subtopics(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


# ------------- Generate Prompt Function -------------

def generate_prompt(curriculum, self_assess, reference1, reference2, reference3, reference4, reference5):
    return f"""
Master Prompt – Biology Rubric Generation
Biology Rubric Generation – Final Working Prompt

Purpose
To generate high-quality, student-ready question and rubric banks for the New Senior Cycle Biology Specification (2025){self_assess}. All outputs must be rigorous, non-repetitive, QA-verified, and practically useful in both teaching and assessment contexts.

Reference Framework

Curriculum Source
- Use the “Students should be able to…” learning outcomes from the Senior Cycle Biology Specification (2025){curriculum}.
- Use the “Students learn about…” column to define scope, terminology, and boundaries.

Reference Materials (for enrichment only)
- {reference1}
- {reference2}
- {reference3}
- {reference4}
- {reference5}

These sources must not be cited, but used to enrich question design, practical application, and conceptual depth.

Question Bank Requirements

Quantity
- Each learning outcome must include 10 non-repetitive questions.

Bloom’s Levels
- Questions must span Bloom’s levels up to and including the level implied by the outcome verb.
- Do not include questions at the Creating level.

Required Variety
Questions must be diverse in form and skill, including:
- Definition recall
- Comparisons (2 terms or processes)
- Text-based diagrams or matching
- Applied scenarios or examples
- Fill-in-the-blanks
- Explanations (only if explicitly prompted)
- Experimental or real-world contexts

Repetition Avoidance
- Each question must target a distinct concept, process, or skill.
- Do not rephrase the same question or use redundant variations.

Rubric Structure

Each question must include:
- Question text (with Bloom’s level indicated)
- Correct Answer
- Rubric table (2 rows, 4 columns) with visible borders:
  | Exceeds Expectations | Meets Expectations | Approaching | Not Yet |

Rubric Assignment Rules

Spelling-Based Rubrics
Use when the correct answer is a single word or short factual label.
Conceptual Rubrics
Use when answers contain multiple parts or terms or require accuracy and specificity.
Explanation-Based Rubrics
Use when a question asks to “explain”, “describe”, “compare”, “why”, “how”, or requires reasoning.

Rubrics must always:
- Be answer-specific
- Match the number of items asked for
- Avoid generic or templated language

Output Format

Word Document (.docx)
- Title: Simplified Rubric Bank – [Code] [Learning Outcome Label]
- Include for each question:
  1. Question (Bloom's Level: [Level])
  2. Question text
  3. Correct Answer: [Answer]
  4. Rubric table with 4 bands as described (horizontal, visible borders)

CSV File (.csv)
- Columns: Question, Bloom's Level, Correct Answer, Exceeds Expectations, Meets Expectations, Approaching, Not Yet

Internal QA Rules (Automatically Applied)
✔ Ensure rubric type matches answer style
✔ Detect explanation-based expectations from question structure
✔ Prevent mismatch between number of items and rubric bands
✔ Remove vague phrases and enforce specific feedback

Always Enrich With:
1. Senior Cycle Biology Specification (2025)
2. OpenStax K12 Biology
3. OpenStax AP Biology Lab Manual
4. Biology Revision & Self Assessment

Action Verbs
Use the Glossary of Action Verbs from the Specification (pages 47–48) to determine cognitive level and response style. All rubric logic must align with the action verb.

Every rubric band must reflect the actual content and phrasing of the correct answer — avoid generic phrasing.
"""


# ------------- Mistral API Function -------------

def call_mistral_api(prompt):
    api_key = "dZVDZitfrDeI2GjNggUiL6yX4OLehZMp"
    if not api_key:
        raise ValueError("Please set the MISTRAL_API_KEY environment variable.")

    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-tiny",  # Replace with your preferred model
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


# ------------- Main Script -------------

def main():
    # File paths
    CURRICULUM_PDF = "Files/SC-BIOLOGY-Spec-ENG.pdf"
    SELF_ASSESS_PDF = "Files/Biology Revision & Self Assessment.pdf"
    REFERENCE1_PDF = "Files/APBiology-OP_5meoFaG.pdf"
    REFERENCE2_PDF = "Files/STUDENT_-_AP_Biology_Lab_Manual_Full.pdf"
    REFERENCE3_PDF = "Files/Biology2e-WEB_ICOFkGu.pdf"
    REFERENCE4_PDF = "Files/ConceptsofBiology-WEB.pdf"
    REFERENCE5_PDF = "Files/Microbiology-WEB.pdf"

    # Extract text from PDFs
    curriculum_text = extract_text_from_pdf(CURRICULUM_PDF)
    self_assess_text = extract_text_from_pdf(SELF_ASSESS_PDF)
    reference1_text = extract_text_from_pdf(REFERENCE1_PDF)
    reference2_text = extract_text_from_pdf(REFERENCE2_PDF)
    reference3_text = extract_text_from_pdf(REFERENCE3_PDF)
    reference4_text = extract_text_from_pdf(REFERENCE4_PDF)
    reference5_text = extract_text_from_pdf(REFERENCE5_PDF)

    # Generate the prompt

    prompt = generate_prompt(
        curriculum_text,
        self_assess_text,
        reference1_text,
        reference2_text,
        reference3_text,
        reference4_text,
        reference5_text
    )

    # Call the Mistral API
    print("Generating questions, answers, and rubrics...")
    response = call_mistral_api(prompt)
    if response:
        print("\n--- Generated Output ---\n")
        print(response)
    else:
        print("No response received.")


if __name__ == "__main__":
    main()
