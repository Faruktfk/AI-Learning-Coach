# AI Learning Coach REST API

This adds a REST API around the existing learning state-machine logic.

The original CLI entry point `app.py` remains unchanged. The API entry point is `api.py`.

## Install

```bash
pip install -r requirements.txt
```

Make sure Ollama is running and the configured model in `services/tools/ollama_client.py` is available.

```bash
ollama serve
ollama pull llama3.2:3b
```

## Start API

From the project root:

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000/docs
```

## Basic flow

### 1. Create session

```bash
curl -X POST http://localhost:8000/sessions
```

### 2. Send topic

```bash
curl -X POST http://localhost:8000/sessions/<SESSION_ID>/step \
  -H "Content-Type: application/json" \
  -d '{"message": "Schwarzes Loch"}'
```

### 3. Run TEACH state

```bash
curl -X POST http://localhost:8000/sessions/<SESSION_ID>/step \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 4. Start quiz

```bash
curl -X POST http://localhost:8000/sessions/<SESSION_ID>/step \
  -H "Content-Type: application/json" \
  -d '{"message": "ja"}'
```

The response contains `data.questions` with options for the UI.

### 5. Submit quiz answers

```bash
curl -X POST http://localhost:8000/sessions/<SESSION_ID>/step \
  -H "Content-Type: application/json" \
  -d '{"answers": [1, 3, 2, 4]}'
```

### 6. Run ADAPT state

```bash
curl -X POST http://localhost:8000/sessions/<SESSION_ID>/step \
  -H "Content-Type: application/json" \
  -d '{}'
```

If the API asks for an adapt decision after repeated failed attempts:

```bash
curl -X POST http://localhost:8000/sessions/<SESSION_ID>/step \
  -H "Content-Type: application/json" \
  -d '{"message": "skip"}'
```

or

```bash
curl -X POST http://localhost:8000/sessions/<SESSION_ID>/step \
  -H "Content-Type: application/json" \
  -d '{"message": "nochmal"}'
```
