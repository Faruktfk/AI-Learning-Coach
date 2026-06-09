# Architektur

## Überblick

AI Learning Coach besteht aus zwei Hauptteilen:

```text
Frontend: React + TailwindCSS
Backend: FastAPI + State Machine + Ollama + Wikipedia-Fetcher + PDF-Generator
```

Das Frontend ist für Darstellung und Interaktion zuständig. Das Backend enthält die fachliche Logik und entscheidet, welcher Schritt als nächstes ausgeführt wird.


## Frontend

Wichtige Dateien:

```text
frontend/src/App.jsx
frontend/src/api/learningApi.js
frontend/src/components/ChatMessage.jsx
frontend/src/components/QuizPanel.jsx
frontend/src/components/LearningProgress.jsx
frontend/src/components/Sidebar.jsx
frontend/src/utils/storage.js
```

Aufgaben des Frontends:

- Lernchats anzeigen
- neue Sessions im Backend erstellen
- REST-Schritte auslösen
- Textfeld oder Buttons abhängig von `input_kind` anzeigen
- Quiz-Fragen einzeln darstellen
- Antworten an das Backend senden
- Markdown im Chat rendern
- PDF-Download anzeigen
- Sidebar, Theme und Konversationen im Browser speichern
- Progress-Bar mit Scroll-Ankern darstellen

## Backend

Wichtige Dateien:

```text
backend/api.py
backend/services/core/api_state_machine.py
backend/services/tools/wiki_fetcher.py
backend/services/tools/ollama_client.py
backend/services/tools/handout_pdf.py
```

Aufgaben des Backends:

- REST-Endpunkte bereitstellen
- Lernsession im RAM verwalten
- Wikipedia-Artikel laden und in Abschnitte zerlegen
- Abschnitt mit dem LLM zusammenfassen
- Multiple-Choice-Fragen mit dem LLM erzeugen
- Antworten auswerten
- Wiederholung, Skip oder Fortschritt entscheiden
- Handout als Markdown erzeugen
- Markdown-Handout als PDF rendern
- PDF-Datei über Download-Endpoint bereitstellen

## Datenfluss

```text
User
  -> React UI
  -> FastAPI Endpoint
  -> LearningSession.step(...)
  -> passender State Handler
  -> ggf. Wikipedia/Ollama/PDF-Generator
  -> StepResult
  -> React UI aktualisiert Chat und Eingabemodus
```

## Zentrale Backend-Klasse

Die wichtigste Klasse ist:

```text
backend/services/core/api_state_machine.py -> LearningSession
```

Eine `LearningSession` entspricht einem Lernchat. Sie enthält:

- aktuelle State-Position
- geladenen Wikipedia-Artikel
- aktuellen Abschnitt
- aktuelle Quizfragen
- letzte Testergebnisse
- ggf. erzeugte Handout-PDF

## Warum eine State Machine?

Die State Machine verhindert, dass das LLM den gesamten Ablauf frei steuert. Stattdessen ist klar definiert, was wann passiert:

- `FETCH` lädt das Thema.
- `TEACH` erklärt einen Abschnitt.
- `CHECK` fragt oder erzeugt einen Test.
- `EVAL` bewertet Antworten.
- `ADAPT` entscheidet Wiederholung oder Fortschritt.
- `HANDOUT` erzeugt das PDF.

Dadurch bleibt das Projekt nachvollziehbar und debugbar.

## Persistenz

Aktuell gibt es zwei Arten von Speicherung:

1. Browser: Konversationen, Theme und Sidebar-Zustand liegen in `localStorage`.
2. Backend: Sessions liegen im Arbeitsspeicher (`SESSIONS` in `api.py`).

Für ein Abschlussprojekt ist das ausreichend, solange die Einschränkung dokumentiert ist. Für produktiven Betrieb wäre eine Datenbank sinnvoll.
