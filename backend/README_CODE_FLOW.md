# Backend-Code einfach erklärt

Der Backend-Code besteht absichtlich aus zwei Ebenen:

1. `api.py` ist nur die REST-Schicht.
   - Erstellt Sessions.
   - Leitet Requests an eine `LearningSession` weiter.
   - Gibt JSON oder das PDF-Handout zurück.

2. `services/core/api_state_machine.py` enthält die eigentliche Lernlogik.
   - Eine `LearningSession` ist genau ein Chat.
   - `step(...)` schaut, welcher Zustand gerade aktiv ist.
   - Danach wird genau eine passende `_handle_*`-Methode ausgeführt.

Die Zustände sind:

```text
FETCH -> TEACH -> CHECK -> EVAL -> ADAPT -> HANDOUT -> FINISHED
```

Bedeutung:

- `FETCH`: Thema entgegennehmen und Wikipedia-Artikel laden.
- `TEACH`: aktuellen Abschnitt zusammenfassen.
- `CHECK`: fragen, ob der Test gestartet werden soll, und Multiple-Choice-Fragen erzeugen.
- `EVAL`: Antworten auswerten und Feedback mit richtiger Lösung erzeugen.
- `ADAPT`: entscheiden, ob wiederholt, übersprungen oder weitergemacht wird.
- `HANDOUT`: PDF-Handout erstellen.
- `FINISHED`: Session ist abgeschlossen.

Wichtig für dich:

- Wenn du die Lernlogik ändern willst, suche zuerst nach der passenden `_handle_*`-Methode.
- Die Frontend-UI entscheidet nichts Fachliches. Sie zeigt nur an, was das Backend zurückgibt.
- `requires_input` und `input_kind` sagen dem Frontend, ob Textfeld, Buttons oder Quiz angezeigt werden sollen.
