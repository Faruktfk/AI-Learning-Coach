# AI Learning Coach Frontend

React + TailwindCSS UI for the FastAPI backend.

## Start

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The backend should run at `http://localhost:8000`.

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

## Behavior

The frontend reads the backend fields `requires_input` and `input_kind`.

- `topic`: normal text input is visible.
- `start_test_decision`: only `Ja` / `Nein` buttons are visible.
- `quiz_answers`: questions are shown one by one, not as a long block.
- `adapt_decision`: only `Nochmal` / `Skip` buttons are visible.

Conversations are stored in `localStorage`, so switching chats does not delete the visible chat history.
