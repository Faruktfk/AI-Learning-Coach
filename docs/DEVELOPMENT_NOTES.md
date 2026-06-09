# Development Notes

Diese Datei sammelt technische Hinweise für spätere Weiterentwicklung.

## Aktuelle Designentscheidung

Das Projekt verwendet bewusst keine komplexe Multi-Agent-Orchestrierung. Stattdessen gibt es eine einfache, nachvollziehbare State Machine.

Vorteile:

- leichter debugbar
- einfacher zu erklären
- besser kontrollierbar
- ausreichend für den aktuellen MVP

## Wichtigste Backend-Datei

```text
backend/services/core/api_state_machine.py
```

Wenn sich der Lernablauf ändern soll, wird meistens diese Datei angepasst.

## Wichtigste Frontend-Datei

```text
frontend/src/App.jsx
```

Diese Datei verbindet Backend-Antworten mit UI-Zuständen und speichert Konversationen im Browser.

## UI-Modi

Das Frontend entscheidet anhand von `input_kind`:

```text
topic                 -> Texteingabe
start_test_decision   -> Ja/Nein-Buttons
quiz_answers          -> QuizPanel
adapt_decision        -> Nochmal/Skip-Buttons
```

## Progress-Bar

Die Progress-Bar basiert auf Metadaten in Chatnachrichten:

```text
progressType: "prompt"
progressType: "section"
progressType: "handout"
```

Der Handout-Schritt gilt erst als abgeschlossen, wenn `progressType: "handout"` vom finalen Handout-State kommt. Eine früh generierte PDF darf den finalen Handout-Schritt nicht als abgeschlossen markieren.

## Handout-Generierung

Es gibt zwei Fälle:

1. Frühe Generierung über `POST /sessions/{session_id}/handout`
2. Finale Generierung im `HANDOUT`-State

Wenn bereits eine PDF existiert, soll sie wiederverwendet werden.

## Mögliche spätere Verbesserungen

- Sessions in SQLite speichern
- PDF-Handouts dauerhaft mit Metadaten verwalten
- User-Accounts einführen
- Wikipedia-Artikel besser vorfiltern
- langen Artikel automatisch in sinnvollere Lerneinheiten splitten
- Tests mit offenen Antworten statt nur Multiple Choice
- bessere Evaluationslogik mit Rubrics
- Deployment mit Docker Compose
