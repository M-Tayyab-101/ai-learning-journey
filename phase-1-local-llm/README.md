# Phase 1 — Local LLM with Ollama + Phi-3

## What I Built

This phase contains my progression from basic experiments to a feature-rich AI assistant, all running the Phi-3 model locally via Ollama.

### 01_basic_chat.py
Simple one-shot chat script that sends a greeting message ("Say hello and tell me what you can do") to Phi-3 and prints the assistant's response content.

### 02_raw_response.py
Basic test script that sends a simple hello message and prints the full raw response object from Ollama (including metadata, not just the text).

### 03_memory_assistant.py
Chat assistant with in-memory conversation history. Maintains a messages list to provide context across the conversation loop, but loses everything when the script ends.

### 04_autosave_assistant.py
Persistent chat assistant that automatically saves the entire conversation to `conversation.json` after every single response, and loads it on startup.

### 05_file_reader_assistant.py
Enhanced assistant that can read text files (.txt, .md), PDFs, and Word documents from a `data` folder. Includes file contents in the conversation context with a 'reload' command to refresh files.

### 06_optimized_assistant.py
Feature-rich assistant with advanced capabilities:
- File caching for better performance
- Daily conversation logs (JSON and text formats)
- Multiple dialogue modes (brief, shorter, very brief replies)
- Automatic math calculation detection and simplified responses
- Learning feedback system that critiques user input
- Commands: help, reload, history, clear, quit

**Note**: Contains bugs with undefined functions (`trim_reply`, `enforce_math_response`) - attempted optimization that revealed bugs, learning moment.

### 07_manual_save_assistant.py
Persistent chat assistant that saves the conversation to `conversation.json` only when the user types 'quit' (manual save), unlike the auto-save version.

## My Exact Setup Steps

1. Downloaded Ollama on C drive via browser
2. Created folder on D drive for Phi-3 model
3. Set environment variable with custom D drive path
4. CMD: `ollama serve` → `ollama run phi3`
5. `pip install open-webui` → `open-webui serve`
6. Browser: http://localhost:8080

## Hardware Used and Why It Became a Bottleneck

- **CPU**: AMD Ryzen 5 PRO 3600
- **RAM**: 8GB
- **GPU**: RX 580 4GB

This hardware became a bottleneck due to insufficient RAM for larger models and processor overheating during extended use. Local LLMs require serious hardware investment to run smoothly.

## What I Learned from This Phase

- How to set up and run local LLMs using Ollama
- Environment variable configuration for custom model paths
- Basic conversation memory implementation
- File I/O integration for context
- The importance of testing and iteration in development
- Hardware limitations are a real constraint for local AI
- Attempted optimizations can introduce bugs (learning from the undefined functions issue)

## Why I Moved On to Cloud APIs

Local LLMs demand significant hardware resources that I didn't have. After experiencing crashes from overheating and slow performance, I diagnosed my own bottleneck and made the decision to pivot to cloud APIs for Phase 2, which would provide scalable computing power without local hardware limitations.