## TODOS:

- CHUNK_QUESTIONS structure: 
	- [{\"question\": \"Frage 1\", \"right_answer\": \"Die richtige Antwort auf Frage 1\"}, {\"question\": \"Frage 2\", \"right_answer\": \"Die richtige Antwort auf Frage 2\"}, ...]
- After eval, dont forget to remove the right answered questions from the CHUNK_QUESTIONS
- After successfull chunk test, dont forget to set ==CHUNK_QUESTIONS to None== and ==increase CHUNK_INDEX==
- 



# Workflow

```txt
User
 ↓
Streamlit Chat UI
 ↓
State Machine
 ↓
PRE_LLM
 ├── Topic Resolver Agent
 └── Wikipedia Fetcher Tool
 ↓
TEACH
 └── Lesson Agent
 ↓
CHECK
 └── Question Generator Agent
 ↓
EVALUATE
 └── Eval Agent
 ↓
ADAPT
 └── Python decision logic
 ↓
ANSWER
 └── Render response in chat

```


---


# File Structure

```txt
adaptive_wiki_tutor/
│
├── app.py
│
├── core/
│   ├── state_machine.py
│   ├── learning_state.py
│   └── adapt.py
│
├── agents/
│   ├── topic_resolver.py
│   ├── lesson_agent.py
│   ├── question_agent.py
│   ├── eval_agent.py
│   └── handout_agent.py
│
├── tools/
│   ├── ollama_client.py
│   └── wiki_fetcher.py
│
├── prompts/
│   ├── topic_resolver.md
│   ├── lesson_agent.md
│   ├── question_agent.md
│   ├── eval_agent.md
│   └── handout_agent.md
│
└── requirements.txt
```

![[ai-tutor-diagramm.png]]