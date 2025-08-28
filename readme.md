This project is to use LLM to analyze a android apk's malicious behavior.



Usage:

 run this command in the project's root path:
 python -m src.main "path_to_apk.apk" "index_name"


path_to_apk.apk is the app to be analyzed
index_name is the app's name stored in vector database
Please NOTE that index_name's first letter must be capital to follow weaviate's requirement.

Because when storing new contents into weaviate database, weaviate will add the new content into the existing content. 
So to convinent future repeat experiment and avoid mix up new content with old, it is neccessary to assign a new index name for every new analyzed app.



Project structure introduction:

1. jadx-1.5.1 is to decompile the apk to obtain the source java code. it's a common used reverse engineering tool. I added it here to convinent project usage.
2. After run the project, a output folder will be created.

    2.1 reverseAPK is the reversed apk after using prementioned jadx. All the app's code and related file will be stored into it. And other preprocess result will also be stored here.

    2.2 APK_info.txt : Some app's infomation extracted from the app to convinent identify the app.

    2.3 LLM_output: LLM's analyze result. There's 4 questions in src\Prompt_and_Question\questions.json, so 4 folders will be created here to store all the analyze result. Each corresponding to a questions analyze conclusion. More questions will be added future based on the experiment result.

    There's will be 2 folders within these 4 folders: retrieve and analyze.
    retrieve is the code been retrieved to be analyzed. As one question may need more than 1 code snippets to be analyzed, each of the retrieve result will be seperatedly stored to prepare for LLM analyzed.
    analyze is the LLM's ananlyze result. 

    On top of that, the question_report.txt is the final report combined all the question's report.

3. src folder placed all the python codes.
    3.1 preprocess: The first step of this project. After decompiled a apk, 4 steps will be conduced:
        java_code_split.py : Split the java code into methods to avoid exceed LLM input limit.
        code_cleaning_summarization.py: Clean the split java code to remove useless code to enhance analyze quality. Generate describtion for each code snippet to describe code's function
        store_vector_datavase: store the description and corresponding code snippets into vector database for further analyze.
        pipeline: organise these step.

        apk_decompile.py : decompile the apk 
        apk_info _extract: extract apk's info
    
    3.2 conversation:
        first_phase.py: retrieve code from the vector database built in prepocess
        first_phase_result_process: split the retrieved code for furture analyze.
        second_phase: call LLM to analyze all the retrieved code and generate reports for each code.

    3.3 Postprocess:
        combine_single_question_report.py: as more than 1 code snippets will be analyzed, this funciton is to combine all the analyzed code into one report.

        Final_report_generation.py : Combine all the questions report together into 1 final report.

        txt2markwon_and_html.pyu : generate markdown file and html to present final report.

    3.4 config.py :
        read the ymal file to retrieve parameters.

    3.5 main.py :
        main file

    3.6 others:
        just some file used when developing.
        





下面是我用GPT整理后的结果


🔍 APK Malicious Behavior Analyzer using LLM

This project leverages Large Language Models (LLMs) to automatically analyze malicious behaviors in Android APKs.

🚀 Usage

Run the following command in the root directory of the project:

python -m src.main "path_to_apk.apk" "IndexName"

Parameters

path_to_apk.apk: Path to the APK file to be analyzed.

IndexName: A unique name used to store the app's information in the vector database.

⚠️ Note:The first letter of IndexName must be capitalized, as required by Weaviate.

💡 Tip:Weaviate adds new content to existing data with the same index name. To avoid mixing new and old results, always use a new index name for each analysis.

📁 Project Structure

project-root/
│
├── jadx-1.5.1/                        # APK decompiler (built-in for convenience)
├── output/
│   ├── reverseAPK/                    # Decompiled APK files and preprocessing results
│   ├── APK_info.txt                   # Extracted app information
│   └── LLM_output/
│       ├── Question1/
│       │   ├── retrieve/              # Retrieved relevant code snippets
│       │   └── analyze/               # LLM analysis results
│       ├── Question2/
│       ├── ...
│       └── question_report.txt        # Combined report for all questions
│
├── src/
│   ├── preprocess/
│   │   ├── java_code_split.py         # Split Java code into methods
│   │   ├── code_cleaning_summarization.py  # Clean code & generate summaries
│   │   ├── store_vector_database.py   # Store vectors into Weaviate
│   │   ├── pipeline.py                # Run full preprocessing pipeline
│   │   ├── apk_decompile.py           # APK decompilation using jadx
│   │   └── apk_info_extract.py        # Extract basic app info
│
│   ├── conversation/
│   │   ├── first_phase.py             # Code retrieval based on prompts
│   │   ├── first_phase_result_process.py  # Prepare code for LLM input
│   │   └── second_phase.py            # LLM analysis and report generation
│
│   ├── postprocess/
│   │   ├── combine_single_question_report.py  # Combine multiple analysis for a question
│   │   ├── final_report_generation.py         # Merge all question reports
│   │   └── txt2markwon_and_html.py            # Export to Markdown/HTML
│
│   ├── config.py                      # Reads parameters from YAML
│   └── main.py                        # Entry point
│
└── (dev files...)                     # Additional development files

🧠 LLM Questions

Located at src/Prompt_and_Question/questions.json, this file contains the predefined questions used to analyze code behavior. Each question generates:

retrieve/: Code snippets relevant to the question.

analyze/: LLM's interpretation and conclusion.

You can expand the questions list as experiments evolve.

📌 Notes

All decompiled code and analysis results are organized automatically.

Final output includes a consolidated report summarizing LLM findings for each question.

HTML and Markdown outputs are available for easy viewing and sharing.