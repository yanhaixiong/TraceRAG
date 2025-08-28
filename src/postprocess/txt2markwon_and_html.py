import os
import markdown

def convert_txt_to_md_and_html(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File does not exist: {file_path}")
        return

    # Generate paths for Markdown and HTML files
    base_name = os.path.splitext(file_path)[0]
    md_file = base_name + ".md"
    html_file = base_name + ".html"

    # Read the text file
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Process text format (convert to Markdown)
    markdown_lines = []
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("#") or stripped_line.startswith("##"):  # Heading
            markdown_lines.append(stripped_line)
        elif stripped_line.startswith("-") or stripped_line.startswith("*"):  # List item
            markdown_lines.append(stripped_line)
        elif stripped_line:  # Normal text
            markdown_lines.append(f"\n{stripped_line}\n")
        else:  # Empty line
            markdown_lines.append("\n")

    # Save as a Markdown file
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_lines))
    print(f"Markdown file saved: {md_file}")

    # Convert Markdown to HTML and save
    with open(md_file, "r", encoding="utf-8") as f:
        md_text = f.read()
    html_content = markdown.markdown(md_text, extensions=["nl2br"])
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML file saved: {html_file}")
