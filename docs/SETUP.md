# Setup und Start

Diese Datei beschreibt, wie das Projekt lokal gestartet wird.

## 1. Voraussetzungen

Empfohlen:

- Python 3.10 oder neuer
- Node.js 18 oder neuer
- npm
- Ollama
- Internetzugang für Wikipedia-Abfragen

## 2. Ollama vorbereiten

Ollama starten:

```bash
ollama serve
```

Modell herunterladen:

```bash
ollama pull llama3.2:3b
```

Falls im Projekt ein anderes Modell in `backend/services/tools/ollama_client.py` konfiguriert ist, muss dieses Modell entsprechend vorhanden sein.

## 3. Backend starten

```bash
cd backend
pip install -r requirements.txt
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Test:

```text
http://localhost:8000/health
```

Erwartete Antwort:

```json
{"status": "ok"}
```

FastAPI-Dokumentation:

```text
http://localhost:8000/docs
```

## 4. Frontend starten

In einem zweiten Terminal:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Die Datei `frontend/.env` sollte enthalten:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Frontend öffnen:

```text
http://localhost:5173
```

## 5. Typischer Testablauf

1. Frontend öffnen.
2. Neues Thema eingeben, z. B. `Schwarzes Loch`.
3. Warten, bis der Wikipedia-Artikel geladen wurde.
4. Einen Abschnitt erklären lassen.
5. Test starten oder überspringen.
6. Multiple-Choice-Fragen beantworten.
7. Nach mehreren Abschnitten optional ein Handout generieren.
8. Am Ende das PDF-Handout herunterladen.

## 6. Häufige Probleme

### Backend nicht erreichbar

Prüfen:

```text
http://localhost:8000/health
```

Wenn keine Antwort kommt, Backend erneut starten.

### Ollama-Modell nicht gefunden

Prüfen:

```bash
ollama list
```

Falls das Modell fehlt:

```bash
ollama pull llama3.2:3b
```

### PDF-Download funktioniert nicht

Prüfen, ob der Download-Link mit `/handouts/...pdf` beginnt und ob das Backend läuft.

### Alte Chats funktionieren nach Backend-Neustart nicht

Das ist aktuell erwartbar, da Backend-Sessions im RAM liegen. Die sichtbare Konversation bleibt im Browser, aber die API-Session existiert nach Neustart nicht mehr.
