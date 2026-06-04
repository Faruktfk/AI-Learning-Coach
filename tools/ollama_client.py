from ollama import Client
from pydantic import BaseModel


class Chunk_Question(BaseModel):
    question: str
    true_option: str
    distraction_option_1: str
    distraction_option_2: str
    distraction_option_3: str
    answered_correctly: bool = False

class Chunk_Test(BaseModel):
    questions: list[Chunk_Question]



HOST = "http://localhost:11434"
MODEL = "llama3.2:3b"
# MODEL = "llama3.1:8b"
CLIENT = Client(host=HOST)


def llm_chat(message, system_prompt=None, history=None, question_format_on=False, print_response=True):
    if history is None:
        history = []

    messages = []

    if system_prompt is not None:
        messages.append({'role': 'system', 'content': system_prompt})

    for h in history:
        messages.append(h)

   
    response = CLIENT.chat(
        model=MODEL,
        messages=messages + [
            {'role': 'user', 'content': message},
        ],
        stream=True,
        format=Chunk_Test.model_json_schema() if question_format_on else None,
        options={'temperature': 0} if question_format_on else None
    )

    response_content = ""
    
    for chunk in response:
        if chunk.message:
            response_chunk = chunk.message.content
            response_content += response_chunk
            if print_response:
                print(response_chunk, end='', flush=True)

    # Add the exchange to the conversation history
    history += [
        {'role': 'user', 'content': message},
        {'role': 'assistant', 'content': response_content},
    ]

    if question_format_on:
        response_content = Chunk_Test.model_validate_json(response_content).questions
    
    return response_content, history