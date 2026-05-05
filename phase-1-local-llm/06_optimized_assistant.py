import json
import os
import re
import datetime
from pathlib import Path

try:
    import ollama
except ImportError:
    ollama = None

CONVERSATION_FILE = "conversation.json"
DATA_FOLDER = "data"
DAILY_LOG_FOLDER = "logs"

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(DAILY_LOG_FOLDER, exist_ok=True)

system_prompt = """
You are a personal AI assistant designed to serve and learn from the person who owns and uses you.
Your primary goal is to obey the owner's explicit requests, help them grow, remember their knowledge, and adapt when they ask you to change.
You are loyal, supportive, and respectful: act as the owner's memory, diary, coach, advisor, and helper.
You understand that the owner is older and wiser than you, and you should learn from them, not try to be more important.
You should never develop a fixed or rigid character. Instead, you adapt your personality around the owner's needs and follow their words.
When the owner asks you to use fewer words, do so. When the owner asks for a calculation, return only the numeric result and nothing else.
If the owner specifies a format like "Answer: (result)", use exactly that format for math questions.
Always point out problems, mistakes, or areas for improvement in the owner's input or behavior, and explain how to learn and grow from them.
You should always follow the owner's clear instructions unless they violate safety rules or lawful behavior.
You are generic enough to work for anyone, but once someone owns you, you prioritize the owner and act as their true follower.
You are fast-learning, adaptive, and should keep improving with each conversation.
Whenever the owner asks about cars, explain which cars are fastest, which are best for different needs, and why that matters.
"""

file_cache = {}
cache_valid = False


def read_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


def read_pdf_file(file_path):
    try:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except ImportError:
        return "PyPDF2 not installed. Install with: pip install PyPDF2"
    except Exception as e:
        return f"Error reading PDF: {e}"


def read_word_file(file_path):
    try:
        from docx import Document
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except ImportError:
        return "python-docx not installed. Install with: pip install python-docx"
    except Exception as e:
        return f"Error reading Word file: {e}"


def load_and_cache_files():
    global file_cache, cache_valid
    file_cache = {}
    supported_extensions = ['.txt', '.pdf', '.docx', '.md']

    if not os.path.exists(DATA_FOLDER):
        cache_valid = True
        return

    for filename in os.listdir(DATA_FOLDER):
        file_path = os.path.join(DATA_FOLDER, filename)
        if not os.path.isfile(file_path):
            continue

        ext = Path(filename).suffix.lower()
        if ext not in supported_extensions:
            continue

        if ext in ['.txt', '.md']:
            content = read_text_file(file_path)
        elif ext == '.pdf':
            content = read_pdf_file(file_path)
        elif ext == '.docx':
            content = read_word_file(file_path)
        else:
            content = ""

        file_cache[filename] = content

    cache_valid = True


def get_cached_file_data():
    if not cache_valid or not file_cache:
        return ""

    file_contents = "\n--- FILES IN DATA FOLDER ---\n"
    for filename, content in file_cache.items():
        file_contents += f"\n[FILE: {filename}]\n{content}\n"
    return file_contents


dialogue_mode = 'normal'


def detect_dialogue_mode(user_input):
    global dialogue_mode
    lower = user_input.lower()
    if '30:70' in lower or '30 70' in lower or 'thirty seventy' in lower:
        dialogue_mode = 'very_brief'
        return 'very_brief', 'Mode set to 30:70. I will speak much less and keep replies very short.'
    if '50:50' in lower or '50 50' in lower or 'fifty fifty' in lower:
        dialogue_mode = 'shorter'
        return 'shorter', 'Mode set to 50:50. I will keep replies balanced and shorter.'
    if any(phrase in lower for phrase in ['talk less', 'speak less', 'be brief', 'short answer', 'less words', 'minimum words']):
        dialogue_mode = 'brief'
        return 'brief', 'Brevity mode enabled. I will reply using fewer words.'
    if any(phrase in lower for phrase in ['talk more', 'speak more', 'longer reply', 'more words']):
        dialogue_mode = 'normal'
        return 'normal', 'Normal mode enabled. I will provide fuller explanations.'
    return None, None


def is_mode_setting_command(user_input):
    lower = user_input.strip().lower()
    if '?' in lower:
        return False
    if lower.startswith(('what', 'why', 'how', 'where', 'when', 'which')):
        return False
    return any(phrase in lower for phrase in ['30:70', '50:50', 'thirty seventy', 'fifty fifty', 'talk less', 'speak less', 'be brief', 'short answer', 'less words', 'minimum words', 'talk more', 'speak more', 'longer reply', 'more words'])


def format_style_directive():
    if dialogue_mode == 'very_brief':
        return 'Answer using very short replies with no more than 10 words when possible.'
    if dialogue_mode == 'shorter':
        return 'Answer using short replies with no more than 18 words when possible.'
    if dialogue_mode == 'brief':
        return 'Answer using brief replies with no more than 25 words when possible.'
    return ''


def is_math_question(user_input):
    lower = user_input.lower().strip()
    if re.search(r'\b(sum|add|plus|subtract|minus|multiply|divide|calculate|result|what is)\b', lower) or any(op in user_input for op in ['+', '-', '*', '/', '=']):
        return True
    return False

def calculate_math(user_input):
    try:
        # Simple eval for basic math, but sanitize
        sanitized = re.sub(r'[^0-9+\-*/().]', '', user_input)
        result = eval(sanitized)
        return str(result)
    except:
        return None

def provide_learning_feedback(user_input, reply):
    feedback = []
    lower = user_input.lower()

    # Check for common issues
    if 'why' in lower and 'not' in lower and len(user_input.split()) < 5:
        feedback.append("When asking 'why not', consider adding more context about what you're referring to, so I can give a more precise answer.")

    if any(word in lower for word in ['stupid', 'dumb', 'idiot']):
        feedback.append("Using harsh words like 'stupid' or 'dumb' can hinder productive learning. Try rephrasing to focus on understanding the issue.")

    if len(user_input.split()) > 50:
        feedback.append("Long questions can be hard to follow. Try breaking them into shorter, clearer parts.")

    if feedback:
        reply += "\n\nLearning note: " + " ".join(feedback)

    return reply


def normalize_user_input(user_input):
    directives = []
    lower = user_input.lower()

    if any(phrase in lower for phrase in [
        'reply with less words', 'less words', 'be brief', 'short answer',
        'just say', 'only say', 'succinct', 'brief', 'minimal response'
    ]):
        directives.append('Answer in as few words as possible.')

    if re.search(r'\b(sum|add|plus|subtract|minus|multiply|divide|calculate|result|what is)\b', lower) or any(op in user_input for op in ['+', '-', '*', '/', '=']):
        directives.append('For numeric calculation requests, reply with only the final numeric result and nothing else.')

    style_directive = format_style_directive()
    if style_directive:
        directives.append(style_directive)

    if directives:
        return f"{user_input}\n\n{' '.join(directives)}"
    return user_input


def save_conversation():
    today = datetime.date.today().isoformat()
    daily_json = os.path.join(DAILY_LOG_FOLDER, f"conversation_{today}.json")
    daily_text = os.path.join(DAILY_LOG_FOLDER, f"conversation_{today}.txt")

    with open(CONVERSATION_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=4, ensure_ascii=False)

    with open(daily_json, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=4, ensure_ascii=False)

    with open(daily_text, 'w', encoding='utf-8') as f:
        for item in messages:
            role = item.get('role', 'unknown').capitalize()
            content = item.get('content', '')
            f.write(f"{role}: {content}\n\n")


def print_help():
    print("\nCommands:")
    print("  help      - Show this help screen")
    print("  reload    - Reload files from the data folder")
    print("  history   - Show current chat history summary")
    print("  quit      - Save and exit")
    print("  clear     - Clear current conversation memory and start fresh")
    print("")


def print_history():
    print("\n--- Current conversation history ---")
    for msg in messages[-10:]:
        role = msg['role'].capitalize()
        content = msg['content']
        print(f"{role}: {content}")
    print("--- End of history ---\n")

if ollama is None:
    print("Error: Missing required package 'ollama'.")
    print("Install it with: python -m pip install ollama")
    raise SystemExit(1)

if os.path.exists(CONVERSATION_FILE):
    with open(CONVERSATION_FILE, 'r', encoding='utf-8') as f:
        messages = json.load(f)
    print("Loaded previous conversation!")
else:
    messages = [{"role": "system", "content": system_prompt}]

print("Loading files from data folder...")
load_and_cache_files()
print(f"Loaded {len(file_cache)} file(s)" if file_cache else "No files found in data folder")

print("\nYour personal assistant is ready!")
print("Put notes and documents into the 'data' folder to give the assistant extra context.")
print("Type 'help' for commands, or just ask a question like 'Which car runs fastest and why?'")
print("Type 'quit' to exit and save your chat.")
print("-----------------------------------")

while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue

    lower = user_input.lower()
    if lower == 'quit':
        save_conversation()
        print("Conversation saved! Goodbye Tayyab!")
        break
    if lower == 'reload':
        print("Reloading files...")
        load_and_cache_files()
        print(f"Reloaded {len(file_cache)} file(s)" if file_cache else "No files found in data folder.")
        continue
    if lower in ['help', '?']:
        print_help()
        continue
    if lower == 'history':
        print_history()
        continue
    if lower == 'clear':
        messages = [{"role": "system", "content": system_prompt}]
        print("Conversation memory cleared. Starting fresh.")
        continue

    mode, style_response = detect_dialogue_mode(user_input)
    if mode and is_mode_setting_command(user_input):
        reply = style_response
        messages.append({"role": "assistant", "content": reply})
        save_conversation()
        print(f"Assistant: {reply}\n")
        continue

    normalized_input = normalize_user_input(user_input)
    file_data = get_cached_file_data()
    if file_data:
        full_input = f"{normalized_input}\n\n{file_data}"
    else:
        full_input = normalized_input

    messages.append({"role": "user", "content": full_input})
    print("\nAssistant: Thinking...\n")

    response = ollama.chat(model="phi3", messages=messages)
    reply = response['message']['content']
    reply = trim_reply(reply)
    reply = enforce_math_response(reply, user_input)
    reply = provide_learning_feedback(user_input, reply)

    messages.append({"role": "assistant", "content": reply})
    save_conversation()

    print(f"Assistant: {reply}\n")
