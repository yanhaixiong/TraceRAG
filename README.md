# 🔍 APK Malicious Behavior Analyzer (TraceRAG)
This project leverages **Large Language Models (LLMs)** to automatically analyze malicious behaviors in Android APKs through code retrieval, cleaning, summarization, and reasoning.

## 🚀 Usage

Run the following command in the project root directory:

```bash
python -m src.main "path_to_apk.apk" "IndexName"
```

**Parameters**

* `path_to_apk.apk`: Path to the APK file to be analyzed.
* `IndexName`: A unique name for storing results in the vector database.

⚠️ **Note**: The first letter of `IndexName` must be capitalized (Weaviate requirement).
💡 **Tip**: Weaviate merges content under the same index name. Always use a **new index name** for each APK to avoid mixing results.

---

## 📁 Project Structure

```
project-root/
│── jadx-1.5.1/                     # APK decompiler (built-in)
│── output/
│   ├── reverseAPK/                 # Decompiled APK files & preprocessing results
│   ├── APK_info.txt                # Extracted app information
│   └── LLM_output/
│       ├── Question1/
│       │   ├── retrieve/           # Retrieved code snippets
│       │   └── analyze/            # LLM analysis results
│       ├── Question2/
│       ├── ...
│       └── question_report.txt     # Combined report across all questions
│── src/
│   ├── preprocess/
│   │   ├── java_code_split.py      # Split Java code into methods
│   │   ├── code_cleaning_summarization.py # Clean & summarize code
│   │   ├── store_vector_database.py# Store vectors in Weaviate
│   │   ├── pipeline.py             # Full preprocessing pipeline
│   │   ├── apk_decompile.py        # APK decompilation
│   │   └── apk_info_extract.py     # Extract basic APK info
│   ├── conversation/
│   │   ├── first_phase.py          # Code retrieval from vector DB
│   │   ├── first_phase_result_process.py # Prepare code for LLM input
│   │   └── second_phase.py         # LLM analysis & report generation
│   ├── postprocess/
│   │   ├── combine_single_question_report.py # Merge multiple analyses per question
│   │   ├── final_report_generation.py        # Consolidated report
│   │   └── txt2markwon_and_html.py          # Export report to Markdown/HTML
│   ├── config.py                   # Load YAML configuration
│   └── main.py                     # Project entry point
└── (dev files...)                  # Extra development scripts
```

---

## 🧠 LLM Questions

* Defined in: `src/Prompt_and_Question/questions.json`
* Each question produces:

  * **retrieve/**: Relevant code snippets
  * **analyze/**: LLM’s reasoning and conclusions
* You can extend this list with new questions as experiments evolve.

---

## 📌 Notes

* All decompiled code, retrievals, and LLM outputs are organized automatically.
* The **final output** includes a consolidated report summarizing findings across all questions.
* Reports can be exported to **Markdown** or **HTML** for easy review and sharing.

---

## 📊 Experimental Data (to be included)

* **TraceRAG\_result.xlsx**
  Contains information on analyzed APKs (benign + malicious):

  * SHA256
  * Reported result
  * Verified result
  * Detected malicious behavior categories
  * Investigation details

* **TraceRAG\_result.zip**

  * Original (uncleaned) source code snippets used in experiments

* **Reports/**

  * Full reports of analyzed APKs

* **queries.txt**

  * Complete record of queries submitted to the LLM

---

## 📌 Future Additions

* **Expanded APK experiment dataset (Excel):**

  * SHA256
  * Size
  * Malware/benign label
  * Malware category
  * Reverse engineering feasibility
  * Inclusion in experiments
  * Number of Java files
  * Number of chunks
  * Other relevant metadata

* **Cleaned code snippets + summarizations**

  * Processed versions of APK code used in experiments

