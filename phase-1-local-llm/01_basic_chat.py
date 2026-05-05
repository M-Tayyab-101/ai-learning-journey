import ollama

response = ollama.chat(
    model="phi3",
    messages=[
        {"role": "user", "content": "Say hello and tell me what you can do"}
    ]
)

print(response['message']['content'])