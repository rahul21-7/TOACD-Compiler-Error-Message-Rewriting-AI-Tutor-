import os
import sys
import re
import json
import time
import argparse
import urllib.request
import urllib.parse
from html.parser import HTMLParser

# --- HTML Parser for SO Post Bodies ---
class SOBodyParser(HTMLParser):
    """
    Parser to extract plain text and code blocks from HTML posts
    returned by the Stack Exchange API.
    """
    def __init__(self):
        super().__init__()
        self.code_blocks = []
        self.text_content = []
        self.in_code = False
        self.current_code = []

    def handle_starttag(self, tag, attrs):
        if tag == "code":
            self.in_code = True

    def handle_endtag(self, tag):
        if tag == "code":
            self.in_code = False
            code_text = "".join(self.current_code).strip()
            if code_text:
                self.code_blocks.append(code_text)
            self.current_code = []

    def handle_data(self, data):
        if self.in_code:
            self.current_code.append(data)
        else:
            self.text_content.append(data)

    def get_clean_text(self):
        # Join text and replace multiple spaces/newlines with a single space
        full_text = "".join(self.text_content)
        return " ".join(full_text.split())

# --- Heuristic Categorization helpers ---
def is_likely_cpp_code(code_str):
    """Checks if a code block is likely C++ source code."""
    cpp_keywords = [
        r'#include', r'std::', r'cout\s*<<', r'cin\s*>>', r'endl', r'int\s+main', 
        r'using\s+namespace', r'vector\s*<', r'struct\s+\w+', r'class\s+\w+',
        r'return\s+\d+;', r'printf\('
    ]
    # Semicolons and brackets check
    structure_score = 0
    if ';' in code_str:
        structure_score += 1
    if '{' in code_str and '}' in code_str:
        structure_score += 1
    
    keyword_matches = sum(1 for kw in cpp_keywords if re.search(kw, code_str))
    
    return keyword_matches >= 1 or structure_score >= 2

def is_likely_compiler_error(code_str):
    """Checks if a code block contains compiler error outputs."""
    error_keywords = [
        r'error:', r'warning:', r'note:', r'ld returned\s+\d+', 
        r'undefined reference to', r'collect2:', r'fatal error:',
        r'\.cpp:\d+:\d+:', r'\^~~~'
    ]
    return any(re.search(kw, code_str, re.IGNORECASE) for kw in error_keywords)

# --- Stack Exchange API Query Helpers ---
def fetch_api_json(url):
    """Fetches JSON content from the Stack Exchange API, handles gzip decoding if needed."""
    headers = {
        "User-Agent": "C++AITutorScraper/1.0"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            encoding = response.info().get('Content-Encoding')
            data = response.read()
            if encoding == 'gzip':
                import gzip
                data = gzip.decompress(data)
            return json.loads(data.decode('utf-8'))
    except Exception as e:
        print(f"Error requesting API: {e}", file=sys.stderr)
        return None

# --- Main scraping pipeline ---
def main():
    parser = argparse.ArgumentParser(description="Scrape Stack Overflow for C++ compiler errors and fixes.")
    parser.add_argument("--limit", type=int, default=10, help="Number of questions to pull (max 100 per page).")
    parser.add_argument("--output", type=str, default="scraped_dataset.json", help="Path to output JSON dataset.")
    parser.add_argument("--api-key", type=str, default=None, help="StackApps API Key to increase quota limit.")
    args = parser.parse_args()

    print(f"Initializing Stack Overflow API scraper (Limit: {args.limit})...")
    
    # Target tag search: c++ AND compiler-errors
    api_url = "https://api.stackexchange.com/2.3/questions?"
    params = {
        "pagesize": min(args.limit, 100),
        "order": "desc",
        "sort": "votes",
        "tagged": "c++;compiler-errors",
        "site": "stackoverflow",
        "filter": "withbody"  # retrieve question text body
    }
    if args.api_key:
        params["key"] = args.api_key
        
    url = api_url + urllib.parse.urlencode(params)
    print(f"Fetching questions from: {url}")
    
    questions_data = fetch_api_json(url)
    if not questions_data or "items" not in questions_data:
        print("Failed to fetch questions from Stack Exchange API.")
        return
        
    items = questions_data["items"]
    print(f"Found {len(items)} questions. Processing and downloading accepted solutions...")

    dataset = []
    
    for idx, item in enumerate(items):
        q_id = item["question_id"]
        title = item["title"]
        body = item["body"]
        accepted_ans_id = item.get("accepted_answer_id")
        
        print(f"[{idx+1}/{len(items)}] Question ID {q_id}: {title}")
        
        if not accepted_ans_id:
            print("  -> No accepted answer. Skipping.")
            continue
            
        # Parse question body
        q_parser = SOBodyParser()
        q_parser.feed(body)
        
        # Categorize question code blocks
        cpp_code_blocks = [cb for cb in q_parser.code_blocks if is_likely_cpp_code(cb)]
        error_blocks = [cb for cb in q_parser.code_blocks if is_likely_compiler_error(cb)]
        
        # Heuristic checks
        error_message = ""
        broken_code = ""
        
        if error_blocks:
            error_message = error_blocks[0]
        elif q_parser.code_blocks:
            # Fallback to the first non-code block if no explicit error layout found
            error_message = q_parser.code_blocks[0]
            
        if cpp_code_blocks:
            broken_code = cpp_code_blocks[0]
        elif q_parser.code_blocks and len(q_parser.code_blocks) > 1:
            broken_code = q_parser.code_blocks[1]
            
        # Clean up empty components
        if not error_message:
            print("  -> Could not isolate compiler error output inside question. Skipping.")
            continue

        # Fetch accepted answer body
        ans_params = {
            "site": "stackoverflow",
            "filter": "withbody"
        }
        if args.api_key:
            ans_params["key"] = args.api_key
            
        ans_url = f"https://api.stackexchange.com/2.3/answers/{accepted_ans_id}?" + urllib.parse.urlencode(ans_params)
        
        # Throttle request rate
        time.sleep(1.0)
        
        ans_data = fetch_api_json(ans_url)
        if not ans_data or "items" not in ans_data or not ans_data["items"]:
            print("  -> Failed to fetch accepted answer. Skipping.")
            continue
            
        ans_item = ans_data["items"][0]
        ans_body = ans_item["body"]
        
        # Parse answer body
        ans_parser = SOBodyParser()
        ans_parser.feed(ans_body)
        
        explanation = ans_parser.get_clean_text()
        
        # Extract corrected code block
        suggested_code = ""
        ans_cpp_blocks = [cb for cb in ans_parser.code_blocks if is_likely_cpp_code(cb)]
        if ans_cpp_blocks:
            suggested_code = ans_cpp_blocks[0]
        elif ans_parser.code_blocks:
            suggested_code = ans_parser.code_blocks[0]
            
        # Structure payload
        data_point = {
            "id": f"so-question-{q_id}",
            "compiler": "gcc",  # standard compiler target
            "error_type": "Compiler Error",
            "error_message": error_message,
            "explanation": explanation[:300] + "..." if len(explanation) > 300 else explanation,
            "suggested_fix": {
                "type": "code_modification" if suggested_code else "documentation_clarification",
                "description": "Adjust the implementation based on the Stack Overflow solution.",
                "code": suggested_code if suggested_code else "Check description for details."
            }
        }
        dataset.append(data_point)
        print(f"  -> Added successfully. Sample error message length: {len(error_message)}")

    if not dataset:
        print("No valid datasets compiled.")
        return
        
    print(f"\nSaving {len(dataset)} items to {args.output}...")
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)
        
    print("Done!")

if __name__ == "__main__":
    main()
