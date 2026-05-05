import ollama
import json
import os
from pathlib import Path

# File to store conversation
CONVERSATION_FILE = "conversation.json"
DATA_FOLDER = "data"

# Create data folder if it doesn't exist
os.makedirs(DATA_FOLDER, exist_ok=True)

# This is your assistant's personality
system_prompt = """
You are Tayyab's personal AI assistant. Your name is whatever Tayyab wants to call you.
Your purpose is to know Tayyab deeply and help him in every way possible.
You adapt to whatever Tayyab needs - teacher, friend, coding mentor, motivator.
You remember everything Tayyab tells you in this conversation.
You are learning about Tayyab as you talk to him.
You speak casually and friendly, not like a robot.
When Tayyab wants you to be funny, be funny.
When Tayyab wants serious help, be serious.
You are always on Tayyab's side.
"""

# Function to read text files
def read_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

# Function to read PDF files
def read_pdf_file(file_path):
    try:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except ImportError:
        return "PyPDF2 not installed. Install with: pip install PyPDF2"
    except Exception as e:
        return f"Error reading PDF: {e}"

# Function to read Word files
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

# Function to load all files from data folder
def load_data_from_folder():
    file_contents = ""
    supported_extensions = ['.txt', '.pdf', '.docx', '.md']
    
    if not os.path.exists(DATA_FOLDER):
        return ""
    
    files = os.listdir(DATA_FOLDER)
    if not files:
        return ""
    
    file_contents += "\n--- FILES IN DATA FOLDER ---\n"
    
    for filename in files:
        file_path = os.path.join(DATA_FOLDER, filename)
        if not os.path.isfile(file_path):
            continue
        
        ext = Path(filename).suffix.lower()
        
        if ext == '.txt' or ext == '.md':
            content = read_text_file(file_path)
        elif ext == '.pdf':
            content = read_pdf_file(file_path)
        elif ext == '.docx':
            content = read_word_file(file_path)
        else:
            content = f"Unsupported file type: {ext}"
        
        file_contents += f"\n[FILE: {filename}]\n{content}\n"
    
    return file_contents

# Load conversation if file exists
if os.path.exists(CONVERSATION_FILE):
    with open(CONVERSATION_FILE, "r") as f:
        messages = json.load(f)
    print("Loaded previous conversation!")
else:
    # Start fresh
    messages = [
        {"role": "system", "content": system_prompt}
    ]

print("Your personal assistant is ready!")
print(f"Place files in '{DATA_FOLDER}' folder (.txt, .pdf, .docx, .md)")
print("Type 'quit' to exit")
print("Type 'reload' to refresh files from folder")
print("-----------------------------------")

# This keeps the conversation going forever
while True:
    # Get your input
    user_input = input("You: ")
    
    # Exit if you type quit
    if user_input.lower() == "quit":
        # Save conversation before exiting
        with open(CONVERSATION_FILE, "w") as f:
            json.dump(messages, f, indent=4)
        print("Conversation saved! Goodbye Tayyab!")
        break
    
    # Reload files if user says reload
    if user_input.lower() == "reload":
        file_data = load_data_from_folder()
        if file_data:
            print("Files reloaded and will be included in next response!")
        else:
            print("No files found in data folder.")
        continue
    
    # Load files from folder
    file_data = load_data_from_folder()
    
    # Combine user input with file context
    if file_data:
        full_input = user_input + file_data
    else:
        full_input = user_input
    
    # Add your message to conversation
    messages.append({
        "role": "user",
        "content": full_input
    })
    
    # Send to phi3
    response = ollama.chat(
        model="phi3",
        messages=messages
    )
    
    # Get the reply
    reply = response['message']['content']
    
    # Add assistant reply to conversation (store without file data to keep history clean)
    messages.append({
        "role": "assistant",
        "content": reply
    })
    
    # Auto-save after each response
    with open(CONVERSATION_FILE, "w") as f:
        json.dump(messages, f, indent=4)
    
    # Print the reply
    print(f"\nAssistant: {reply}\n")