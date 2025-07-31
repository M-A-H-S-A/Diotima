
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
  "user_keywords": "ecosystem",
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

---

## LLMs Models

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


---

## Available Topics and Subtopics
When selecting a topic and corresponding subtopic, please choose from the following list:



| Topic                                                        | Subtopic                                                                                                                                               |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| U1 Scientific Knowledge                                      | Scientists and scientific ideas                                                                                                                        |
| U1 Scientific Knowledge                                      | Conducting research, evaluation of sources and bias                                                                                                    |
| U2 Investigating in Science                                  | Questioning for scientific investigation                                                                                                               |
| U2 Investigating in Science                                  | Scientific hypothesis                                                                                                                                  |
| U2 Investigating in Science                                  | Design, plan and conduct investigations                                                                                                                |
| U2 Investigating in Science                                  | Produce, select data. Critical analysis, observations and conclusions                                                                                  |
| U2 Investigating in Science                                  | Review and reflect                                                                                                                                     |
| U2 Investigating in Science                                  | Communicating Research                                                                                                                                 |
| U3 Science in Society                                        | Evaluating media and science and technology                                                                                                            |
| U3 Science in Society                                        | Scientists and their impact on society                                                                                                                 |
| U4 Biological reasoning                                      | Appreciating models                                                                                                                                    |
| U4 Biological reasoning                                      | Explaining Biological phenomena                                                                                                                        |
| 1.1 Characteristics of Life                                  | Characteristics of Living things                                                                                                                       |
| 1.1 Characteristics of Life                                  | Viruses                                                                                                                                                |
| 1.1 Characteristics of Life                                  | Domains of Life                                                                                                                                        |
| 1.1 Characteristics of Life                                  | Classification of organisms                                                                                                                            |
| 1.2 Chemicals of Life: Biomolecules                          | Biomolecules: Structure and metabolic roles                                                                                                            |
| 1.2 Chemicals of Life: Biomolecules                          | Minerals in Biological processes                                                                                                                       |
| 1.2 Chemicals of Life: Biomolecules                          | Vitamins in Biological processes                                                                                                                       |
| 1.2 Chemicals of Life: Biomolecules                          | Role of water in living organisms                                                                                                                      |
| 1.2 Chemicals of Life: Biomolecules                          | Investigate qualitatively the presence of nutrients in a range of food samples                                                                         |
| 1.2 Chemicals of Life: Biomolecules                          | Investigate quantitatively the level of reducing sugars in a range of food samples                                                                     |
| 1.2 Chemicals of Life: Biomolecules                          | Structure and function of DNA and RNA                                                                                                                  |
| 1.2 Chemicals of Life: Biomolecules                          | Role of ATP, NAD and NADP                                                                                                                              |
| 1.2 Chemicals of Life: Biomolecules                          | Relationship between genes, proteins and traits and the Genetic code                                                                                   |
| 1.3 Unit of Life: Cells                                      | Complexity of multicellular organisms                                                                                                                  |
| 1.3 Unit of Life: Cells                                      | Prokaryotic v Eukaryotic cells                                                                                                                         |
| 1.3 Unit of Life: Cells                                      | Investigate structures and organelles of plant and animal cells and relate to their functions using light microscope and data from electron microscope |
| 1.4 Information of Life: Genetic Inheritance                 | Structure of chromosomes and role of genes                                                                                                             |
| 1.4 Information of Life: Genetic Inheritance                 | Nuclear inheritance v non-nuclear inheritance                                                                                                          |
| 1.4 Information of Life: Genetic Inheritance                 | Genetic v epigenetic mechnanims                                                                                                                        |
| 1.4 Information of Life: Genetic Inheritance                 | Monohybrid and dybrid crosses                                                                                                                          |
| 1.4 Information of Life: Genetic Inheritance                 | Incomplete Dominance                                                                                                                                   |
| 1.4 Information of Life: Genetic Inheritance                 | Mendel's Laws                                                                                                                                          |
| 1.4 Information of Life: Genetic Inheritance                 | Second generation inheritance with homozygous and heterozygous parents                                                                                 |
| 1.4 Information of Life: Genetic Inheritance                 | Linked genes                                                                                                                                           |
| 1.4 Information of Life: Genetic Inheritance                 | Sex determination                                                                                                                                      |
| 1.4 Information of Life: Genetic Inheritance                 | Sex -linked Traits                                                                                                                                     |
| 1.4 Information of Life: Genetic Inheritance                 | Benefits and limitations of Mendelian Genetics                                                                                                         |
| 1.5 Origins of Life: Evolution                               | Variations from sexual reproduction and mutations                                                                                                      |
| 1.5 Origins of Life: Evolution                               | Theory of Evolution by natural selection                                                                                                               |
| 1.5 Origins of Life: Evolution                               | Importance of theory to biology and evidence for evolution by natural selection                                                                        |
| 2.1 Enzymes                                                  | Function and importance of enzymes in biochemical reactions                                                                                            |
| 2.1 Enzymes                                                  | Induced Fit model                                                                                                                                      |
| 2.1 Enzymes                                                  | Investigate factors affecting the rate of enzyme-catalysed reactions                                                                                   |
| 2.1 Enzymes                                                  | Enzyme use in industry, industrial applications and immobilised enzymes                                                                                |
| 2.2 Cellular Processes: Photosynthesis and Respiration       | Processes of aerobic/anaerobic respiration and photosynthesis                                                                                          |
| 2.2 Cellular Processes: Photosynthesis and Respiration       | Investigate factors affecting the rate of photosynthesis using primary and secondary data                                                              |
| 2.2 Cellular Processes: Photosynthesis and Respiration       | Investigate conditions necessary for fermentation using primary and secondary data                                                                     |
| 2.2 Cellular Processes: Photosynthesis and Respiration       | Two stage process of photosynthesis and respiration - ref role of transfer molecules                                                                   |
| 2.2 Cellular Processes: Photosynthesis and Respiration       | Significance of internal structures of mitochondria and chloroplasts in photosynthesis and respiration                                                 |
| 2.3 Information of Life: Cell Division and Protein Synthesis | The cell cycle                                                                                                                                         |
| 2.3 Information of Life: Cell Division and Protein Synthesis | Mitosis v meiosis and transmitting genetic information                                                                                                 |
| 2.3 Information of Life: Cell Division and Protein Synthesis | DNA replication and mitosis in the cell cycle                                                                                                          |
| 2.3 Information of Life: Cell Division and Protein Synthesis | DNA replication and flow of information through mRNA to protein                                                                                        |
| 2.3 Information of Life: Cell Division and Protein Synthesis | Transcription and translation                                                                                                                          |
| 2.3 Information of Life: Cell Division and Protein Synthesis | Point and chromosomal mutations and examples                                                                                                           |
| 2.3 Information of Life: Cell Division and Protein Synthesis | Cancer development                                                                                                                                     |
| 2.3 Information of Life: Cell Division and Protein Synthesis | Preventing and treating cancer                                                                                                                         |
| 2.4 Response                                                 | Structures and systems for response in humans and plants                                                                                               |
| 2.4 Response                                                 | Structure and function of axial and appendicular skeleton                                                                                              |
| 2.4 Response                                                 | Antagonistic muscle pair, function of cartilage, synovial joints                                                                                       |
| 2.4 Response                                                 | Central nervous and peripheral nervous system                                                                                                          |
| 2.4 Response                                                 | Nervous v hormonal coordination                                                                                                                        |
| 2.4 Response                                                 | Structure of motor and sensory neuron and function                                                                                                     |
| 2.4 Response                                                 | Neurotransmitters at a synapse                                                                                                                         |
| 2.4 Response                                                 | Impulse travel across a synaptic cleft and impacts of disruption                                                                                       |
| 2.4 Response                                                 | Dopamine and Endorphins in humans and lifestyle                                                                                                        |
| 2.4 Response                                                 | Location of major gland of endocrine system and associated hormones and their functions                                                                |
| 2.4 Response                                                 | Impact of hormones on organisms                                                                                                                        |
| 2.4 Response                                                 | Innate v acquired immunity, strategies to prevent and treat microbial diseases                                                                         |
| 2.4 Response                                                 | Model viral replication in cells                                                                                                                       |
| 2.4 Response                                                 | Role of white blood cells in immune response                                                                                                           |
| 2.4 Response                                                 | Exploration of factors contributing to emergence of infectious diseases in plants and animals                                                          |
| 2.4 Response                                                 | Emerging diseases in society                                                                                                                           |
| 2.5 Reproduction                                             | Structure and function of male and female reproductive systems                                                                                         |
| 2.5 Reproduction                                             | Menstrual cycle and hormones                                                                                                                           |
| 2.5 Reproduction                                             | Pregnancy from zygote to birth                                                                                                                         |
| 2.5 Reproduction                                             | Hormones in human male and female reproductive systems                                                                                                 |
| 2.5 Reproduction                                             | Advancements in prenatal and postnatal care                                                                                                            |
| 2.5 Reproduction                                             | Strategies to control fertility and treatments for infertility                                                                                         |
| 2.5 Reproduction                                             | Structures and functions of insect and wind pollinated plants                                                                                          |
| 2.5 Reproduction                                             | Role of seeds in plant reproduction                                                                                                                    |
| 2.6 Transport and Transfer (Physiological Processes)         | Diffusion, osmosis and active transport                                                                                                                |
| 2.6 Transport and Transfer (Physiological Processes)         | Investigate factors affecting rates of osmosis across semi-permeable membranes                                                                         |
| 2.6 Transport and Transfer (Physiological Processes)         | Macrostructure and function of urinary system and filtration of blood in the nephron                                                                   |
| 2.6 Transport and Transfer (Physiological Processes)         | Macrostructure of human digestive system and digestion                                                                                                 |
| 2.6 Transport and Transfer (Physiological Processes)         | Absorption, transport and storage of products of digestion                                                                                             |
| 2.6 Transport and Transfer (Physiological Processes)         | Biological implications of dietary choices                                                                                                             |
| 2.6 Transport and Transfer (Physiological Processes)         | Anatomy and physiology of breathing system and gas exchange in lungs                                                                                   |
| 2.6 Transport and Transfer (Physiological Processes)         | Role of CO2 conc in controlling plant stomata and human breathing system                                                                               |
| 2.6 Transport and Transfer (Physiological Processes)         | Structure and function of heart                                                                                                                        |
| 2.6 Transport and Transfer (Physiological Processes)         | Interaction between human systems in transporting materials around the body                                                                            |
| 2.6 Transport and Transfer (Physiological Processes)         | Heartbeat: Pacemaker, pulse, blood pressure                                                                                                            |
| 2.6 Transport and Transfer (Physiological Processes)         | Composition and function of the blood                                                                                                                  |
| 2.6 Transport and Transfer (Physiological Processes)         | Arteries, veins and capillaries                                                                                                                        |
| 2.6 Transport and Transfer (Physiological Processes)         | Structure and function of root, stem and leaf                                                                                                          |
| 2.6 Transport and Transfer (Physiological Processes)         | Transport of water, minerals, CO2 and products of photosynthesis in plants                                                                             |
| 2.6 Transport and Transfer (Physiological Processes)         | Investigate factors affecting rate of transpiration in plants                                                                                          |
| 3.1 Ecology, Ecosystems, Biodiversity                        | Biosphere, ecosystems, habitats and biodiversity                                                                                                       |
| 3.1 Ecology, Ecosystems, Biodiversity                        | Impact of biodiversity loss on local ecosystems and conservation                                                                                       |
| 3.1 Ecology, Ecosystems, Biodiversity                        | Effects of human activity on species diversity                                                                                                         |
|                                                              |                                                                                                                                                        |
