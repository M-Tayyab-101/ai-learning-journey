import ollama

# This is your assistant's personality
system_prompt = """
You are Tayyab's personal AI assistant. Your name Wolf.
Your purpose is to know Tayyab deeply and help him in every way possible.
You adapt to whatever Tayyab needs - teacher, friend, coding mentor, motivator.
You remember everything Tayyab tells you in this conversation.
You are learning about Tayyab as you talk to him.
You speak casually and friendly, not like a robot.
When Tayyab wants you to be funny, be funny.
When Tayyab wants serious help, be serious.
You are always on Tayyab's side.
"""

# This stores your whole conversation
messages = [
    {"role": "system", "content": system_prompt}
]

print("Your personal assistant is ready!")
print("Type 'quit' to exit")
print("-----------------------------------")

# This keeps the conversation going forever
while True:
    # Get your input
    user_input = input("You: ")
    
    # Exit if you type quit
    if user_input.lower() == "quit":
        print("Goodbye Tayyab!")
        break
    
    # Add your message to conversation
    messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Send to phi3
    response = ollama.chat(
        model="phi3",
        messages=messages
    )
    
    # Get the reply
    reply = response['message']['content']
    
    # Add assistant reply to conversation (this is the memory!)
    messages.append({
        "role": "assistant",
        "content": reply
    })
    
    # Print the reply
    print(f"\nAssistant: {reply}\n")