from ollama import Client
import os


HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")

CLIENT = Client(host=HOST)

def llm_chat(message, system_prompt=None, history=None):
    if history is None:
        history = []

    messages = []

    if system_prompt is not None:
        messages.append({'role': 'system', 'content': system_prompt})

    for h in history:
        messages.append(h)

    response_content = ""
    
    response = CLIENT.chat(
        model=MODEL,
        messages=messages + [
            {'role': 'user', 'content': message},
        ],
        stream=True
    )
    for chunk in response:
        if chunk.message:
            response_chunk = chunk.message.content
            response_content += response_chunk
    
    # Add the exchange to the conversation history
    history += [
        {'role': 'user', 'content': message},
        {'role': 'assistant', 'content': response_content},
    ]
    
    return response_content, history