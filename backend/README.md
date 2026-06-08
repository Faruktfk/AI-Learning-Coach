# AI Learning Coach

Wikipedia-basierter Lerncoach mit FastAPI Backend und React/Tailwind Frontend.

## Backend starten

```bash
pip install -r requirements.txt
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Ollama muss parallel laufen:

```bash
ollama serve
ollama pull llama3.2:3b
```

API-Doku:

```text
http://localhost:8000/docs
```

## Frontend starten

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## Wichtige Features

- ChatGPT-ähnliche Chat-Oberfläche
- Dark-/Light-Theme
- Chatverläufe bleiben beim Wechseln erhalten (`localStorage`)
- Assistentenantworten werden visuell Wort für Wort angezeigt
- Tests werden Frage für Frage angezeigt
- Bei Ja/Nein, Multiple Choice und Nochmal/Skip verschwindet das Eingabefeld
- Handout-State generiert ein PDF und stellt es als Download-Link bereit

## Hinweis

Backend-Sessions liegen aktuell im Arbeitsspeicher. Die sichtbaren Chatverläufe bleiben im Browser erhalten, aber nach einem Backend-Neustart können alte API-Sessions nicht mehr fortgesetzt werden. Für produktiven Betrieb wäre später SQLite/PostgreSQL sinnvoll.
