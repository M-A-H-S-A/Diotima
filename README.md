
#  General Prompt Generator

This repository contains `main.py` — a flexible educational Q&A and rubric generator that uses LLMs (like Mistral or OpenAI GPT) to produce high-quality question-answer pairs and marking rubrics for any subject.

---

##  How It Works

- It loads:
  - **parameters.json** — your main inputs (subject, topic, subtopic, Bloom’s level, etc.).
  - **book.json** — textbook excerpts to give the model context.
  - **curriculum.json** — curriculum expectations to help align questions.
  - **examples.json** — example Q&As to guide style.
  - **rubrics.json** — a rubric template.

- You can add or skip any of these — the model will fall back to its general knowledge if they’re missing.

- The script reads your **API config** (model & API key) from `config.json`.

- The final prompt is sent to your chosen LLM (Mistral or OpenAI).

- The response (questions, answers, rubrics) is saved as `output.json` in your output folder.

---

##  Project Structure

```
/your-project
├── main.py
├── config.json
├── parameters.json
├── data/
│   ├── biology/
│   │   ├── book.json
│   │   ├── curriculum.json
│   │   ├── examples.json
│   │   ├── rubrics.json
│   ├── chemistry/
│       ├── ...
└── results/
    └── output.json
```

- `main.py` — your main script.
- `config.json` — holds your API key and model info.
- `parameters.json` — all your user inputs.
- `data/subject/` — any supporting files for that subject.
- `results/` — generated Q&A and rubrics.

---

##  Example `config.json`

```json
{
  "provider": "mistral",
  "api_key": "YOUR_API_KEY"
}
```

Or for OpenAI:

```json
{
  "provider": "openai",
  "api_key": "YOUR_OPENAI_API_KEY"
}
```

---

##  Example `parameters.json`

```json
{
  "subject": "Biology",
  "grade_level": "10",
  "topic": "Photosynthesis",
  "subtopic": "Light Reactions",
  "bloom_level": "Understand",
  "num_questions": 5,
  "user_keywords": "chlorophyll, ATP, NADPH",
  "output_folder": "results"
}
```

---

##  How to Run


Fill in your API key and provider in `config.json`.

Adjust parameters in `parameters.json`.

 Run the script:

```bash
python main.py
```

Find your generated Q&A & rubrics in the `results/` folder as `output.json`.

