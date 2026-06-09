# REST API

Die API wird mit FastAPI bereitgestellt.

Basis-URL lokal:

```text
http://localhost:8000
```

API-Dokumentation:

```text
http://localhost:8000/docs
```

## Health Check

```http
GET /health
```

Antwort:

```json
{"status": "ok"}
```

## Session erstellen

```http
POST /sessions
```

Erstellt eine neue `LearningSession` im Backend.

Beispielantwort:

```json
{
  "session_id": "...",
  "state_before": "FETCH",
  "state_after": "FETCH",
  "message": "Welches Thema möchtest du lernen?...",
  "requires_input": true,
  "input_kind": "topic",
  "data": {},
  "download_url": null,
  "session": {
    "current_state": "FETCH"
  }
}
```

## Session-Snapshot abrufen

```http
GET /sessions/{session_id}
```

Gibt den aktuellen Zustand einer Session zurück. Hinweis: Sessions liegen aktuell im RAM.

## Lernschritt ausführen

```http
POST /sessions/{session_id}/step
Content-Type: application/json
```

Request-Felder:

```json
{
  "message": "optional text",
  "answers": [1, 2, 3]
}
```

Typische Verwendung:

### Thema senden

```json
{"message": "Schwarzes Loch"}
```

### Nächsten automatischen Schritt ausführen

```json
{}
```

### Test starten

```json
{"message": "ja"}
```

### Test überspringen

```json
{"message": "nein"}
```

### Quiz-Antworten senden

```json
{"answers": [1, 3, 2, 4]}
```

### Adapt-Entscheidung senden

```json
{"message": "nochmal"}
```

oder:

```json
{"message": "skip"}
```

## Handout frühzeitig generieren

```http
POST /sessions/{session_id}/handout
```

Erzeugt ein PDF-Handout, ohne den normalen Lernzustand zu verändern. Falls bereits eine PDF existiert, wird sie wiederverwendet.

## Handout herunterladen

```http
GET /handouts/{filename}
```

Liefert die generierte PDF-Datei aus. Dieser Download hängt nicht von der In-Memory-Session ab, sondern nur davon, ob die PDF-Datei im Handout-Ordner existiert.

## Response-Felder

Alle zentralen Lern-Endpunkte geben ein gemeinsames Format zurück:

```json
{
  "session_id": "...",
  "state_before": "TEACH",
  "state_after": "CHECK",
  "message": "...",
  "requires_input": false,
  "input_kind": null,
  "data": {},
  "download_url": null,
  "session": {}
}
```

Bedeutung:

- `message`: Text für den Chat
- `requires_input`: ob die UI auf User-Eingabe warten soll
- `input_kind`: welcher UI-Modus angezeigt werden soll
- `data`: Zusatzdaten, z. B. Quizfragen oder Abschnittstitel
- `download_url`: relativer Link zur PDF-Datei
- `session`: Snapshot des Backend-Zustands
