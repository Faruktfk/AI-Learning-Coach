from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from services.tools import ollama_client, wiki_fetcher
from services.tools.handout_pdf import build_handout_filename, create_one_page_handout_pdf


STATES = ["FETCH", "TEACH", "CHECK", "EVAL", "ADAPT", "HANDOUT", "FINISHED"]


@dataclass
class StepResult:
    session_id: str
    state_before: str
    state_after: str
    message: str
    requires_input: bool = False
    input_kind: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    download_url: Optional[str] = None
    session: Dict[str, Any] = field(default_factory=dict)


class LearningSession:
    """
    API-friendly wrapper around the existing learning logic.

    The original CLI state machine is based on input()/print(). This class keeps
    the same state flow and decision logic, but returns JSON-ready StepResult
    objects instead of printing directly to the terminal.
    """

    def __init__(self) -> None:
        self.session_id = str(uuid.uuid4())
        self.state_index = 0
        self.lesson_content: Optional[Dict[str, Any]] = None
        self.current_chunk_index = 0
        self.chunk_questions = None
        self.chunk_test_tries = 0
        self.latest_question_payload: List[Dict[str, Any]] = []
        self.last_score: Optional[Dict[str, Any]] = None
        self.handout_text: Optional[str] = None
        self.handout_pdf_path: Optional[Path] = None

    def get_current_state(self) -> str:
        return STATES[self.state_index]

    def snapshot(self) -> Dict[str, Any]:
        current_title = None
        article_title = None
        section_count = 0

        if self.lesson_content is not None:
            article_title = self.lesson_content.get("title")
            section_count = len(self.lesson_content.get("sections", []))

            if self.current_chunk_index < section_count:
                current_title = self.lesson_content["sections"][self.current_chunk_index].get("title")

        return {
            "session_id": self.session_id,
            "current_state": self.get_current_state(),
            "current_chunk_index": self.current_chunk_index,
            "chunk_test_tries": self.chunk_test_tries,
            "article_title": article_title,
            "current_chunk_title": current_title,
            "section_count": section_count,
            "handout_ready": self.handout_pdf_path is not None,
        }

    def initial_response(self) -> StepResult:
        return self._result(
            state_before="FETCH",
            message=(
                "Welches Thema möchtest du lernen? Bitte gib ein spezifisches Thema an, "
                "z.B. 'Quantenphysik', 'Photosynthese' oder 'Renaissance Kunst'."
            ),
            requires_input=True,
            input_kind="topic",
        )

    def step(self, message: Optional[str] = None, answers: Optional[List[int]] = None) -> StepResult:
        current_state = self.get_current_state()

        if current_state == "FETCH":
            return self._handle_fetch(message)

        if current_state == "TEACH":
            return self._handle_teach()

        if current_state == "CHECK":
            return self._handle_check(message)

        if current_state == "EVAL":
            return self._handle_eval(answers)

        if current_state == "ADAPT":
            return self._handle_adapt(message)

        if current_state == "HANDOUT":
            return self._handle_handout()

        return self._result(
            state_before=current_state,
            message="Diese Lernsession ist bereits abgeschlossen.",
            requires_input=False,
            input_kind=None,
            download_url=self._download_url(),
        )

    def _handle_fetch(self, message: Optional[str]) -> StepResult:
        state_before = "FETCH"

        if message is None or not message.strip():
            return self.initial_response()

        user_input = message.strip()

        if user_input.lower() == "exit":
            self.state_index = STATES.index("FINISHED")
            return self._result(
                state_before=state_before,
                message="Lernassistent wird beendet. Auf Wiedersehen!",
            )

        if len(user_input.split(" ")) <= 3:
            resolved_topic = user_input
        else:
            resolved_topic, _ = ollama_client.llm_chat(
                system_prompt=(
                    "Du bist ein hilfreicher Assistent, der die Benutzereingabe in spezifische Lernthemen auflöst. "
                    "Wenn die Eingabe bereits ein spezifisches Thema ist, gib es unverändert zurück. Selbst wenn die "
                    "Benutzereingabe vage ist, versuche ein spezifisches Thema zu inferieren, das recherchiert und gelernt "
                    "werden kann. Gib nur das aufgelöste Thema ohne zusätzlichen Text zurück. DU DARFST KEINE ERKLÄRUNGEN "
                    "ODER ZUSÄTZLICHEN INFORMATIONEN GEBEN, NUR DAS AUFGELOSTE THEMENTITEL. DU DARFST AUßERDEM DEN "
                    "THEMENTITEL AUCH NICHT IN EIGENEN WORTEN UMFORMULIEREN, WENN DER THEMENTITEL BEREITS SPEZIFISCH "
                    "GENUG IST. WENN DIE BENUTZEREINGABE Z.B. 'QUANTENPHYSIK' IST, GIB 'QUANTENPHYSIK' ZURÜCK, NICHTS ANDERES."
                ),
                message=user_input,
                print_response=False,
            )
            resolved_topic = resolved_topic.strip()

        try:
            self.current_chunk_index = 0
            self.chunk_test_tries = 0
            self.chunk_questions = None
            self.latest_question_payload = []
            self.lesson_content = wiki_fetcher.get_wikipedia_article(resolved_topic, lang="de")

            chunk_titles = " | ".join(section["title"] for section in self.lesson_content["sections"])

            self.state_index = STATES.index("TEACH")
            return self._result(
                state_before=state_before,
                message=(
                    f"Aufgelöstes Thema: {resolved_topic}\n\n"
                    f"Gelesener Wikipedia-Artikel: {self.lesson_content['title']}\n\n"
                    f"Artikel in folgende Abschnitte unterteilt:\n{chunk_titles}\n\n"
                    "Der Lernassistent beginnt nun mit dem ersten Abschnitt. Viel Erfolg beim Lernen!"
                ),
                data={
                    "resolved_topic": resolved_topic,
                    "article_title": self.lesson_content["title"],
                    "chunk_titles": [section["title"] for section in self.lesson_content["sections"]],
                },
            )
        except Exception as exc:
            self.state_index = STATES.index("FETCH")
            return self._result(
                state_before=state_before,
                message=(
                    f"Fehler beim Abrufen des Wikipedia-Artikels: {exc}\n\n"
                    "Bitte versuche es erneut mit einem anderen Thema oder überprüfe deine Internetverbindung."
                ),
                requires_input=True,
                input_kind="topic",
            )

    def _handle_teach(self) -> StepResult:
        state_before = "TEACH"

        if self.lesson_content is None:
            self.state_index = STATES.index("FETCH")
            return self.initial_response()

        if self.current_chunk_index >= len(self.lesson_content["sections"]):
            self.current_chunk_index = 0
            self.state_index = STATES.index("HANDOUT")
            return self._result(
                state_before=state_before,
                message="Alle Abschnitte des Artikels wurden durchgearbeitet.",
            )

        point_of_focus = None
        if self.chunk_questions is not None:
            questions = ", ".join([item.question for item in self.chunk_questions])
            point_of_focus = [
                {
                    "role": "user",
                    "content": (
                        "In der nächsten Zusammenfassung sollst du dich auf die folgenden Fragen konzentrieren: "
                        f"[{questions}]. Wenn du die folgenden Informationen zusammenfasst, versuche besonders die "
                        "Informationen hervorzuheben, die für die Beantwortung dieser Fragen relevant sind."
                    ),
                }
            ]

        section = self.lesson_content["sections"][self.current_chunk_index]
        chunk_summary, _ = ollama_client.llm_chat(
            system_prompt=(
                "Du bist ein hilfreicher Lernassistent, der die folgenden Informationen in einfachen Worten zusammenfasst, "
                "damit ein Schüler sie verstehen kann. Fasse die folgenden Informationen zusammen:\n\n{message}\n\n"
                "Gib nur die Zusammenfassung zurück, ohne zusätzliche Erklärungen oder Informationen. DU DARFST KEINE "
                "ERKLÄRUNGEN ODER ZUSÄTZLICHEN INFORMATIONEN GEBEN, NUR DIE ZUSAMMENFASSUNG DER WICHTIGSTEN PUNKTE "
                "DER INFORMATIONEN, DIE IN EINFACHEN WORTEN FORMULIERT IST, DAMIT EIN SCHÜLER SIE VERSTEHEN KANN. "
                "DIE LÄNGE DER ZUSAMMENFASSUNG SOLL MINIMAL 10 UND MAXIMAL 20 SÄTZE BETRAGEN."
            ),
            message=section["content"],
            history=point_of_focus,
            print_response=False,
        )
        section["summary"] = chunk_summary

        self.state_index = STATES.index("CHECK")
        return self._result(
            state_before=state_before,
            message=f"{self.current_chunk_index + 1}. {section['title'].upper()}\n\n{chunk_summary}",
            data={
                "chunk_index": self.current_chunk_index,
                "chunk_title": section["title"],
                "summary": chunk_summary,
            },
        )

    def _handle_check(self, message: Optional[str]) -> StepResult:
        state_before = "CHECK"

        if message is None or not message.strip():
            section_title = self._current_section_title()
            return self._result(
                state_before=state_before,
                message=f"Möchtest du den Test für den Abschnitt {self.current_chunk_index + 1} ({section_title}) starten?",
                requires_input=True,
                input_kind="start_test_decision",
                data={"options": ["ja", "nein"]},
            )

        user_input = message.strip().lower()

        if user_input == "nein":
            self.chunk_test_tries = 0
            self.chunk_questions = None
            self.latest_question_payload = []
            self.current_chunk_index += 1
            self.state_index = STATES.index("TEACH")
            return self._result(
                state_before=state_before,
                message="Okay, der Test wird übersprungen.",
            )

        section = self.lesson_content["sections"][self.current_chunk_index]
        self.chunk_questions, _ = ollama_client.llm_chat(
            system_prompt=(
                "Du bist ein hilfreicher Lernassistent, der basierend auf den folgenden Informationen 3 bis 8 "
                "Multiple-Choice-Fragen generiert, um das Verständnis eines Schülers zu überprüfen. Generiere Fragen, "
                "die sich auf die wichtigsten Punkte der Informationen konzentrieren und das Verständnis des Schülers testen. "
                "DU DARFST KEINE ERKLÄRUNGEN ODER ZUSÄTZLICHEN INFORMATIONEN GEBEN. DU SOLLST DIE FRAGEN IN FOLGENDEN "
                "FORMAT GENERIEREN: JEDES FRAGE-ANTWORT-SET SOLL EIN DICT SEIN, DAS DIE FOLGENDEN FELDER ENTHÄLT: "
                "'question' (die Frage), 'true_option' (die richtige Antwortoption), 'distraction_option_1' (eine falsche "
                "Antwortoption), 'distraction_option_2' (eine falsche Antwortoption) und 'distraction_option_3' (eine falsche "
                "Antwortoption). GIB NUR DIE FRAGEN IM ANGEGEBENEN JSON-FORMAT ZURÜCK, OHNE ZUSÄTZLICHE ERKLÄRUNGEN "
                "ODER INFORMATIONEN."
            ),
            message=section["summary"],
            question_format_on=True,
            print_response=False,
        )

        self.latest_question_payload = self._build_question_payload()
        self.state_index = STATES.index("EVAL")

        return self._result(
            state_before=state_before,
            message=f"Der Test für Abschnitt {self.current_chunk_index + 1} ist bereit. Beantworte die Fragen nacheinander.",
            requires_input=True,
            input_kind="quiz_answers",
            data={
                "chunk_index": self.current_chunk_index,
                "chunk_title": section["title"],
                "tries": self.chunk_test_tries,
                "questions": self.latest_question_payload,
            },
        )

    def _handle_eval(self, answers: Optional[List[int]]) -> StepResult:
        state_before = "EVAL"

        if not answers:
            return self._result(
                state_before=state_before,
                message="Bitte beantworte zuerst die Testfragen.",
                requires_input=True,
                input_kind="quiz_answers",
                data={"questions": self.latest_question_payload},
            )

        if self.chunk_questions is None:
            self.state_index = STATES.index("CHECK")
            return self._result(
                state_before=state_before,
                message="Es sind keine Testfragen vorhanden. Der Test wird neu vorbereitet.",
            )

        correct_count = 0
        results = []

        for index, question in enumerate(self.chunk_questions):
            selected_option_id = answers[index] if index < len(answers) else None
            payload_question = self.latest_question_payload[index]
            selected_option = None

            for option in payload_question["options"]:
                if option["id"] == selected_option_id:
                    selected_option = option
                    break

            is_correct = selected_option is not None and selected_option["text"] == question.true_option
            question.answered_correctly = is_correct
            if is_correct:
                correct_count += 1

            results.append(
                {
                    "question_id": index + 1,
                    "question": question.question,
                    "selected_option_id": selected_option_id,
                    "selected_option_text": selected_option["text"] if selected_option else None,
                    "true_option": question.true_option,
                    "answered_correctly": is_correct,
                }
            )

        total = len(self.chunk_questions)
        correct_percentage = correct_count / total if total else 0
        self.last_score = {
            "correct_count": correct_count,
            "total": total,
            "correct_percentage": correct_percentage,
            "results": results,
        }

        self.state_index = STATES.index("ADAPT")

        return self._result(
            state_before=state_before,
            message=f"Du hast {correct_count} von {total} Fragen richtig beantwortet. ({correct_percentage:.2%})",
            data=self.last_score,
        )

    def _handle_adapt(self, message: Optional[str]) -> StepResult:
        state_before = "ADAPT"

        if self.last_score is None:
            self.state_index = STATES.index("CHECK")
            return self._result(
                state_before=state_before,
                message="Es liegt noch keine Auswertung vor. Der Test wird neu vorbereitet.",
            )

        correct_percentage = self.last_score["correct_percentage"]

        if correct_percentage < 0.5:
            # Third or later try: old CLI asked immediately for nochmal/skip.
            if self.chunk_test_tries >= 3 and (message is None or not message.strip()):
                return self._result(
                    state_before=state_before,
                    message=(
                        "Es scheint, dass du Schwierigkeiten mit diesem Abschnitt hast. Es ist in Ordnung.\n\n"
                        "Möchtest du den Abschnitt nochmals versuchen oder zum nächsten Abschnitt übergehen?"
                    ),
                    requires_input=True,
                    input_kind="adapt_decision",
                    data={"options": ["nochmal", "skip"]},
                )

            # If user responded to the third-try decision.
            if self.chunk_test_tries >= 3 and message is not None:
                user_input = message.strip().lower()
                if user_input == "skip":
                    self.chunk_test_tries = 0
                    self.chunk_questions = None
                    self.latest_question_payload = []
                    self.current_chunk_index += 1
                    self.state_index = STATES.index("TEACH")
                    return self._result(
                        state_before=state_before,
                        message="Okay, lass uns zum nächsten Abschnitt übergehen.",
                    )

                self.state_index = STATES.index("TEACH")
                return self._result(
                    state_before=state_before,
                    message="Okay, lass es uns nochmals durchgehen.",
                )

            self.chunk_test_tries += 1
            self.chunk_questions = [q for q in self.chunk_questions if not q.answered_correctly]
            self.latest_question_payload = []

            if self.chunk_test_tries < 3:
                self.state_index = STATES.index("TEACH")
                return self._result(
                    state_before=state_before,
                    message=(
                        "Es scheint, dass du Schwierigkeiten mit diesem Abschnitt hast. "
                        "Lass es uns nochmals durchgehen und versuchen, die Informationen besser zu verstehen."
                    ),
                )

            return self._result(
                state_before=state_before,
                message=(
                    "Es scheint, dass du Schwierigkeiten mit diesem Abschnitt hast. Es ist in Ordnung.\n\n"
                    "Möchtest du den Abschnitt nochmals versuchen oder zum nächsten Abschnitt übergehen?"
                ),
                requires_input=True,
                input_kind="adapt_decision",
                data={"options": ["nochmal", "skip"]},
            )

        self.chunk_test_tries = 0
        self.chunk_questions = None
        self.latest_question_payload = []
        self.current_chunk_index += 1
        self.state_index = STATES.index("TEACH")

        return self._result(
            state_before=state_before,
            message="Gut gemacht! Lass uns zum nächsten Abschnitt übergehen.",
        )

    def _handle_handout(self) -> StepResult:
        state_before = "HANDOUT"

        if self.lesson_content is None:
            self.state_index = STATES.index("FETCH")
            return self.initial_response()

        if self.handout_pdf_path is None:
            self.handout_text = self._generate_handout_text()
            self.handout_pdf_path = build_handout_filename(self.session_id, self.lesson_content["title"])
            create_one_page_handout_pdf(
                title=self.lesson_content["title"],
                handout_text=self.handout_text,
                output_path=self.handout_pdf_path,
            )

        self.state_index = STATES.index("FINISHED")
        return self._result(
            state_before=state_before,
            message=(
                "HERZLICHEN GLÜCKWUNSCH! DU HAST ALLE ABSCHNITTE DURCHGEARBEITET!\n\n"
                "Dein Handout wurde als PDF generiert und steht jetzt zum Download bereit."
            ),
            data={"handout_text": self.handout_text},
            download_url=self._download_url(),
        )

    def _generate_handout_text(self) -> str:
        assert self.lesson_content is not None

        summaries = []
        for section in self.lesson_content["sections"]:
            summary = section.get("summary")
            if summary:
                summaries.append(f"## {section['title']}\n{summary}")

        source_text = "\n\n".join(summaries)

        if not source_text.strip():
            source_text = "\n\n".join(
                f"## {section['title']}\n{section['content'][:900]}"
                for section in self.lesson_content["sections"]
            )

        try:
            handout, _ = ollama_client.llm_chat(
                system_prompt=(
                    "Du bist ein hilfreicher Lernassistent. Erstelle ein kompaktes, gut strukturiertes Lern-Handout "
                    "auf Deutsch. Das Handout soll maximal eine PDF-Seite lang sein. Nutze kurze Überschriften und "
                    "Bulletpoints. Konzentriere dich auf die wichtigsten Begriffe, Zusammenhänge und Merksätze. "
                    "Gib nur den Handout-Text zurück, ohne Zusatzkommentar."
                ),
                message=(
                    f"Artikel: {self.lesson_content['title']}\n\n"
                    f"Zusammenfassungen der bearbeiteten Abschnitte:\n\n{source_text}"
                ),
                print_response=False,
            )
            return handout.strip()
        except Exception:
            return self._fallback_handout_text(source_text)

    def _fallback_handout_text(self, source_text: str) -> str:
        assert self.lesson_content is not None
        lines = [f"# {self.lesson_content['title']}", "", "Wichtigste Punkte:"]
        for section in self.lesson_content["sections"][:8]:
            summary = section.get("summary") or section.get("content", "")[:350]
            summary = " ".join(summary.split())
            lines.append(f"- {section['title']}: {summary[:220]}")
        return "\n".join(lines)

    def _build_question_payload(self) -> List[Dict[str, Any]]:
        payload = []

        for index, question in enumerate(self.chunk_questions or [], start=1):
            options = [
                question.true_option,
                question.distraction_option_1,
                question.distraction_option_2,
                question.distraction_option_3,
            ]
            random.shuffle(options)

            payload.append(
                {
                    "id": index,
                    "question": question.question,
                    "options": [
                        {"id": option_index, "text": option_text}
                        for option_index, option_text in enumerate(options, start=1)
                    ],
                }
            )

        return payload

    def _current_section_title(self) -> str:
        if self.lesson_content is None:
            return ""
        if self.current_chunk_index >= len(self.lesson_content["sections"]):
            return ""
        return self.lesson_content["sections"][self.current_chunk_index]["title"]

    def _download_url(self) -> Optional[str]:
        if self.handout_pdf_path is None:
            return None
        return f"/sessions/{self.session_id}/handout.pdf"

    def _result(
        self,
        state_before: str,
        message: str,
        requires_input: bool = False,
        input_kind: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        download_url: Optional[str] = None,
    ) -> StepResult:
        return StepResult(
            session_id=self.session_id,
            state_before=state_before,
            state_after=self.get_current_state(),
            message=message,
            requires_input=requires_input,
            input_kind=input_kind,
            data=data or {},
            download_url=download_url,
            session=self.snapshot(),
        )
