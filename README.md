# AI Learning Coach

AI Learning Coach ist ein Wikipedia-basierter Lernassistent mit einem FastAPI-Backend und einem React/Tailwind-Frontend. Die Anwendung führt Lernende schrittweise durch einen Wikipedia-Artikel: Thema eingeben, Artikel laden, Abschnitt erklären, Test durchführen, Ergebnis auswerten, adaptiv wiederholen oder fortfahren und am Ende ein PDF-Handout herunterladen.

## Kernidee

Das Projekt bildet einen einfachen Lehrer-Schüler-Ablauf als State Machine ab:

```text
FETCH -> TEACH -> CHECK -> EVAL -> ADAPT -> HANDOUT -> FINISHED
```

Die fachliche Lernlogik liegt im Backend. Das Frontend zeigt nur den aktuellen Zustand an und entscheidet anhand von `requires_input` und `input_kind`, ob ein Texteingabefeld, Ja/Nein-Buttons, Multiple-Choice-Fragen oder Nochmal/Skip-Buttons sichtbar sind.

## Features

- ChatGPT-ähnliche Oberfläche mit React und TailwindCSS
- Dark-/Light-Theme mit Speicherung im Browser
- einklappbare Sidebar mit gespeicherten Lernverläufen
- Wort-für-Wort-Anzeige nur für neue Assistentenantworten
- Markdown-Rendering im Chat
- Frage-für-Frage-Quiz mit direkter farblicher Korrektur
- rechte schrittweise Progress-Bar mit Scroll-Ankern
- Handout-PDF-Generierung am Ende oder optional schon vorher
- PDF-Download über FastAPI
- Wikipedia-Artikel als Lernquelle
- Ollama als lokales LLM-Backend

## Projektstruktur

```text
AI-Learning-Coach/
├── backend/
│   ├── api.py
│   ├── app.py
│   ├── requirements.txt
│   └── services/
│       ├── core/
│       │   ├── api_state_machine.py
│       │   └── state_machine.py
│       └── tools/
│           ├── handout_pdf.py
│           ├── ollama_client.py
│           └── wiki_fetcher.py
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api/
│   │   ├── components/
│   │   └── utils/
│   └── public/
└── docs/
    ├── assets/
    │   └── ai-tutor-diagramm.png
    ├── ARCHITECTURE.md
    ├── API.md
    ├── STATE_MACHINE.md
    ├── SETUP.md
    └── FINAL_CHECKLIST.md
```

## Diagramm

Lege dein Zustandsdiagramm hier ab:

```text
docs/assets/ai-tutor-diagramm.png
```

Es wird in der Architektur- und State-Machine-Dokumentation referenziert.

## Voraussetzungen

- Python 3.10 oder neuer empfohlen
- Node.js 18 oder neuer empfohlen
- Ollama installiert und gestartet
- ein lokal verfügbares Ollama-Modell, z. B. `llama3.2:3b`

## Backend starten

```bash
cd backend
pip install -r requirements.txt
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Ollama muss parallel laufen:

```bash
ollama serve
ollama pull llama3.2:3b
```

API-Dokumentation:

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

Die Datei `frontend/.env` sollte enthalten:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Aktuelle Einschränkungen

- Backend-Sessions liegen aktuell im Arbeitsspeicher. Nach einem Backend-Neustart können alte Browser-Konversationen sichtbar bleiben, aber die zugehörige API-Session existiert nicht mehr.
- Browser-Verläufe werden in `localStorage` gespeichert und sind daher nur lokal im jeweiligen Browser verfügbar.
- Wikipedia-Inhalte sind nicht didaktisch kuratiert. Manche Artikelabschnitte können zu kurz, zu lang oder ungeeignet sein.
- LLM-Ausgaben können trotz strukturierter Prompts variieren.

## Wichtige Dokumente

- [`docs/SETUP.md`](docs/SETUP.md): Installation und Start
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): Architekturüberblick
- [`docs/STATE_MACHINE.md`](docs/STATE_MACHINE.md): Zustände und Lernablauf
- [`docs/API.md`](docs/API.md): REST-Endpunkte
