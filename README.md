---

# 🔍 APK Malicious Behavior Analyzer (TraceRAG)

This project leverages **Large Language Models (LLMs)** to analyze Android APKs and detect potential malicious behaviors. It integrates APK reverse engineering, code preprocessing, vector database retrieval, and multi-phase LLM reasoning to generate structured security reports. Please refer to [link](https://arxiv.org/abs/2509.08865) for our paper under review titled `TraceRAG: A LLM-Based Framework for Explainable Android Malware Detection and Behavior Analysis`. 

---

## 🚀 Usage

Run the following command in the project’s root directory:

```bash
python -m src.main "path_to_apk.apk" "IndexName"
```

**Parameters**

* `path_to_apk.apk`: The APK file to be analyzed.
* `IndexName`: The name under which the app’s information is stored in the vector database.

⚠️ **Important**: The first letter of `IndexName` must be capitalized (Weaviate requirement).
💡 **Tip**: Weaviate appends new content to existing entries. To ensure repeatable experiments and avoid mixing new/old data, assign a **new `IndexName`** for every APK analysis.

---

## 📁 Project Structure

### Root Level

* **jadx-1.5.1/**
  A widely used APK decompiler. Included here for convenience to directly decompile APKs into Java source code.

* **output/**
  This folder is created automatically after analysis. It contains:

  * **reverseAPK/**: Decompiled APK (via JADX), including all Java code, resources, and preprocessing results.
  * **APK\_info.txt**: Extracted metadata (e.g., package name, version) for quick identification.
  * **LLM\_output/**: Organized results of LLM analysis.

    * Each question in `src/Prompt_and_Question/questions.json` generates a dedicated subfolder:

      * **retrieve/**: Code snippets retrieved for that question.
      * **analyze/**: LLM’s reasoning results on retrieved snippets.
    * **question\_report.txt**: Aggregated report across all predefined questions.

---

### Source Code (src/)

* **preprocess/**
  The first step after APK decompilation. Four main scripts are executed sequentially:

  * `java_code_split.py`: Splits Java source files into methods to avoid exceeding LLM input limits.
  * `code_cleaning_summarization.py`: Cleans irrelevant code (e.g., boilerplate) and generates short descriptions for each method.
  * `store_vector_database.py`: Stores descriptions + corresponding code snippets into the Weaviate vector database.
  * `pipeline.py`: Organizes and executes the full preprocessing workflow.
  * `apk_decompile.py`: Handles APK decompilation using JADX.
  * `apk_info_extract.py`: Extracts app metadata (e.g., package, permissions).

* **conversation/**
  Implements a two-phase reasoning process:

  * `first_phase.py`: Retrieves candidate code snippets from the vector database based on prompts/questions.
  * `first_phase_result_process.py`: Splits and formats the retrieved snippets for further analysis.
  * `second_phase.py`: Calls LLM to analyze snippets and generates per-question reports.

* **postprocess/**
  Consolidates partial results into human-readable reports:

  * `combine_single_question_report.py`: Merges multiple snippet analyses into one report for a given question.
  * `final_report_generation.py`: Combines all question reports into one final security report.
  * `txt2markwon_and_html.py`: Converts results into Markdown and HTML formats for easy sharing.

* **config.py**
  Loads parameters (e.g., API keys, database config) from YAML.

* **main.py**
  Project entry point.

* **(dev files)**
  Additional experimental or helper scripts used during development.

---

## 🧠 LLM Questions

The file `src/Prompt_and_Question/questions.json` defines the **set of questions** used to analyze malicious behaviors (e.g., sensitive API usage, dynamic loading, privilege escalation).

For each question:

* **retrieve/** contains relevant code snippets.
* **analyze/** contains the LLM’s interpretation and reasoning.

These questions are extendable, allowing the framework to adapt as experiments evolve.

---

## 📌 Notes

* All steps—decompilation, preprocessing, retrieval, and analysis—are automated once you run `main.py`.
* The **final output** is a structured report that consolidates findings across all questions.
* Results can be exported into **Markdown** and **HTML** formats for convenient review and presentation.

---

## 📊 Experimental Data (to be included)

* **TraceRAG\_result.xlsx**
  Records benign APKs used in experiments, with columns:

  * SHA256
  * Report result
  * Verified result
  * Detected malicious behavior categories (if any)
  * Detailed investigation notes

* **TraceRAG\_result.zip**
  Contains raw (uncleaned) source code snippets of APKs used in the experiments.

* **Reports/**
  Stores the generated reports of APKs.

* **queries.txt**
  Contains all queries submitted to the LLM during experiments.

---

## 🔮 Future Additions

* Expanded **APK experiment dataset** (Excel) with metadata:

  * SHA256, size, malware/benign label
  * Malware category (if applicable)
  * Reverse engineering feasibility
  * Whether included in experiments
  * Number of Java files / chunks (if processed)
  * Other useful metadata

* **Cleaned code snippets + summaries** of APKs for systematic benchmarking.
