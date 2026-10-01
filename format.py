import re
import sys

def reformat_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Matches an optional carriage return, newline, the language name, 
    # optional spaces/newlines, and the opening ```
    pattern = r'\r?\n([a-zA-Z0-9_-]+)\s*\r?\n\s*```'
    
    # Replaces the match so the language is inside the backticks: ```Bash
    updated_content = re.sub(pattern, r'\n```\1', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_markdown_file>")
        sys.exit(1)
    
    reformat_markdown(sys.argv[1])
    print(f"Successfully reformatted {sys.argv[1]}")