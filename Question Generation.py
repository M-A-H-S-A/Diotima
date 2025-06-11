import os
import re
import yaml
import pandas as pd
import fitz  # PyMuPDF
from mistralai import Mistral


# --------- Config & File Loaders ---------

def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_text_file(path):
    if path and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading text file '{path}': {e}")
    else:
        print(f"⚠️ Text file not found: {path}")
    return ""


def read_pdf(path):
    if path and os.path.exists(path):
        try:
            doc = fitz.open(path)
            return "".join(page.get_text() for page in doc)
        except Exception as e:
            print(f"Error reading PDF '{path}': {e}")
    else:
        print(f"⚠️ PDF not found: {path}")
    return ""


# --------- Prompt Creation ---------

def generate_prompt(cfg, curriculum, self_assess, reference):
    parts = [f"- Subject: {cfg['subject']}", f"- Topic: {cfg['topic']}"]
    if cfg.get("subtopic"):
        parts.append(f"- Subtopic: {cfg['subtopic']}")

    bloom_levels = cfg.get("diff_level", {})
    if not bloom_levels:
        raise ValueError("diff_level config missing or empty")

    if cfg.get("past_exam_questions"):
        parts.append(f"- Past exam questions: {cfg['past_exam_questions']}")

    header = "\n".join(parts)

    prompt = f"""
MASTER PROMPT – BIOLOGY RUBRIC GENERATION

You are an AI assistant helping a teacher create high-quality exam questions. Please generate high-quality assessment questions with rubrics according to the following criteria:

{header}

GUIDELINES:

1. For each Bloom’s Taxonomy level listed below, generate the specified number of questions.
2. Each question must include:
   • Question Text (mention Bloom level)
   • Correct Answer
   • A 4-column rubric table with labels:
     | Exceeds Expectations | Meets Expectations | Approaching | Not Yet |

3. Rubrics:
   - Spelling-based: single-word answers
   - Conceptual: multiple terms or parts
   - Explanation-based: requires reasoning
   - Internal QA Rules (Automatically Applied)
   - Ensure rubric type matches answer style
   - Detect explanation-based expectations from question structure
   - Prevent mismatch between number of items and rubric bands
   - Remove vague phrases and enforce specific feedback
   - Every rubric band must reflect the actual content and phrasing of the correct answer — avoid generic phrasing.


4. Format questions numbered separately for each level, like:
   ### Question 1 ({{level}})
   **Question Text ({{level}}):** ...
   **Correct Answer:** ...
   | Exceeds Expectations | Meets Expectations | Approaching | Not Yet |
   |----------------------|--------------------|-------------|---------|
   | … | … | … | … |

5. Question variety: include definitions, comparisons, scenarios, diagrams, etc.
6. No repetition. No extra text outside the questions. Use Markdown.

"""

    for level, num_q in bloom_levels.items():
        prompt += f"\n--- Bloom’s Level: {level} — Generate {num_q} questions ---\n"

    if curriculum:
        prompt += f"\n--- Curriculum Snippet ---\n{curriculum[:1000]}\n"
    if self_assess:
        prompt += f"\n--- Self-Assessment Snippet ---\n{self_assess[:1000]}\n"
    if reference:
        prompt += f"\n--- Reference Snippet ---\n{reference[:1000]}\n"

    prompt += "\nProceed with the questions now."
    return prompt


# --------- Mistral Call ---------

def call_mistral(prompt, api_key):
    with Mistral(api_key=api_key) as client:
        resp = client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}],
        )
    return resp.choices[0].message.content.strip()


# --------- Save to CSV ---------

def save_to_csv(text, folder, filename="questions.csv"):
    os.makedirs(folder, exist_ok=True)
    # Split questions by "### Question <num> (<level>)" pattern to keep bloom level tags
    entries = re.split(r"###\s*Question\s*\d+\s*\([^)]+\)", text)
    # Sometimes the split leaves an empty first entry, so remove empties
    questions = [e.strip() for e in entries if e.strip()]

    df = pd.DataFrame({"Question": questions})
    path = os.path.join(folder, filename)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"✅ Saved {len(questions)} questions to {path}")


# --------- Main ---------

def main():
    cfg = load_config()

    curriculum = read_text_file(cfg.get("curriculum_file", ""))
    self_assess = read_pdf(cfg.get("self_assessment_pdf", ""))
    reference = read_pdf(cfg.get("reference_file", ""))

    prompt = generate_prompt(cfg, curriculum, self_assess, reference)
    print("➡️ Sending prompt to Mistral...")
    output = call_mistral(prompt, cfg["api_key"])
    print("\n--- Output preview ---\n")
    print(output[:800] + "\n...")

    save_to_csv(output, cfg["output_folder"])


if __name__ == "__main__":
    main()
