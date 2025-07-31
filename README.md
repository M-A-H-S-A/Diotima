
#  General Prompt Generator

This repository contains `main.py` — a flexible educational Q&A and rubric generator that uses LLMs (like Mistral or OpenAI GPT) to produce high-quality question-answer pairs and marking rubrics for any subject.

---

##  How It Works

- It loads:
  - **parameters.json** — main inputs (subject, topic, subtopic, Bloom’s level, etc.).
  - **book.json** — textbook excerpts to give the model context.
  - **curriculum.json** — curriculum expectations to help align questions.
  - **examples.json** — example Q&As to guide style.
  - **rubrics.json** — a rubric template.

- You can add or skip any of these — the model will fall back to its general knowledge if they’re missing.

- The script reads the **API config** (model & API key) from `config.json`.

- The final prompt is sent to your chosen LLM (Mistral or OpenAI ...).

- The response (questions, answers, rubrics) is saved as `output.json` in:
  `/data/<subject>/results/<output_folder>/`

- Logs token usage (input/output tokens and time) to token_log.csv in the output folder.

- Ignores rubric generation for specific question types like "multiple_choice", "true_false", etc., defined in rubrics.json.

- Rubric generation aligns with ideal answers and cognitive frameworks like Bloom, SOLO, and VALUE.

---

##  Project Structure

```
edu_content_generator/
├── main.py
├── config.json
├── parameters.json
├── src/                         # All core logic modules
│   ├── __init__.py
│   ├── config_loader.py
│   ├── data_loader.py
│   ├── prompt_builder.py
│   ├── llm_api_client.py
│   ├── output_processor.py
│   └── token_logger.py
├── data/
│   ├── __init__.py
│   └── biology/
│       ├── __init__.py
│       ├── book.json
│       ├── curriculum.json
│       ├── examples.json
│       ├── rubrics.json
│       └── results/            
│           └── <output_folder>/
│               ├── output.json
│               └── token_log.csv



```

- `main.py` —  main script.
- `config.json` — holds the API key and model info.
- `parameters.json` — all the user inputs.
- `data/subject/` — any supporting files for that subject.
- `results/` — generated Q&A and rubrics.

---

##  Example `config.json`

```json
{
  "model": "gpt-4o",
  "mistral_api_key": "YOUR_Mistral_API_KEY",
  "openai_api_key": "YOUR_Openai_API_KEY",
  "gemini_api_key": "YOUR_Gemini_API_KEY",
  "meta_llama_api_key": "LLM|YOUR_META_LLAMA_API_KEY_HERE"

}
```
---

##  Example `parameters.json`

```json
{
  "subject": "Biology",
  "grade_level": "10",
  "topic": "3.3 Information of life: genetic engineering",
  "subtopic": "Scientific hypothesis",
  "bloom_level": "Remembering",
  "num_questions": 4,
  "user_keywords": "",
  "output_folder": "Test"
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


In this example, the output will be saved in:
/data/biology/results/Enzymes/output.json

###_______________________________________________________###


List of model names you can use in the `config.json`, grouped by provider.

**1. Google Gemini (for `gemini_api_key`)**

* `models/gemini-2.5-flash`
* `models/gemini-2.5-flash-lite`
* `models/gemini-2.5-pro`
* `models/gemini-1.5-flash`
* `models/gemini-1.5-pro`
* `models/gemini-pro`
* `models/gemini-pro-vision` (for multimodal input including images)

**2. OpenAI (for `openai_api_key`)**

* `gpt-4o`
* `gpt-4o-mini`
* `gpt-4-turbo` (or `gpt-4-turbo-2024-04-09` for a specific date version)
* `gpt-3.5-turbo` (or `gpt-3.5-turbo-0125` for a specific date version)

**3. Mistral AI (for `mistral_api_key`)**

* `mistral-large-latest`
* `mistral-small-latest`
* `mistral-medium-latest`
* `mixtral-8x7b-instruct-v0.1`
* `codestral-2501`
* `mistral-nemo`

**4. Ollama (No separate API key needed, requires local download via `ollama pull <model_name>`)**

* `llama3`
* `mistral`
* `mixtral`
* `gemma`
* `phi3`
* `codellama`
