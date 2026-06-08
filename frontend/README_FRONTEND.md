# AI Learning Coach Frontend

React + TailwindCSS UI for the AI Learning Coach REST API.

The design is intentionally ChatGPT-like:

- left sidebar with sessions
- central chat conversation
- fixed bottom composer
- no text input when the API expects fixed choices
- button-only interaction for `ja/nein`, `nochmal/skip`, and quiz options

## Start backend

From the project root:

```bash
pip install -r requirements.txt
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

## Start frontend

From the `frontend` folder:

```bash
npm install
cp .env.example .env
npm run dev
```

Open:

```text
http://localhost:5173
```

## Environment

The frontend reads the backend URL from:

```text
VITE_API_BASE_URL=http://localhost:8000
```

## API interaction model

The frontend calls:

```http
POST /sessions
POST /sessions/{session_id}/step
GET  /sessions
DELETE /sessions/{session_id}
```

It decides which input UI to show by reading:

```json
{
  "requires_input": true,
  "input_kind": "topic | start_test_decision | quiz_answers | adapt_decision"
}
```

Mapping:

| `input_kind` | UI |
|---|---|
| `topic` | text input |
| `start_test_decision` | `ja/nein` buttons |
| `quiz_answers` | multiple-choice buttons |
| `adapt_decision` | `nochmal/skip` buttons |

## Note about session history

The current backend keeps session state in memory but does not persist full chat history. Therefore, if you select an older session in the sidebar, the frontend can continue the state, but it cannot reconstruct all previous chat messages unless the backend later stores messages.
