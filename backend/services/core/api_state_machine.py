import random
from typing import Any, Dict, List, Optional
from uuid import uuid4

from services.tools import ollama_client
from services.tools import wiki_fetcher


STATES = ["FETCH", "TEACH", "CHECK", "EVAL", "ADAPT", "HANDOUT"]


def _question_to_dict(question: Any) -> Dict[str, Any]:
    """Convert a Pydantic question object or dict to a JSON-safe dict."""
    if hasattr(question, "model_dump"):
        return question.model_dump()
    if isinstance(question, dict):
        return dict(question)
    return {
        "question": getattr(question, "question", ""),
        "true_option": getattr(question, "true_option", ""),
        "distraction_option_1": getattr(question, "distraction_option_1", ""),
        "distraction_option_2": getattr(question, "distraction_option_2", ""),
        "distraction_option_3": getattr(question, "distraction_option_3", ""),
        "answered_correctly": getattr(question, "answered_correctly", False),
    }


def _set_answered_correctly(question: Any, value: bool) -> None:
    if isinstance(question, dict):
        question["answered_correctly"] = value
    else:
        question.answered_correctly = value


def _get_question_attr(question: Any, name: str) -> Any:
    if isinstance(question, dict):
        return question.get(name)
    return getattr(question, name)


class LearningSession:
    """
    API-friendly wrapper around the existing CLI state-machine logic.

    Important:
    - The learning decisions are intentionally kept equivalent to your CLI code.
    - input()/print() are replaced by request/response fields.
    - One instance represents one learning session.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid4())

        self.state_index = 0
        self.lesson_content: Optional[Dict[str, Any]] = None
        self.current_chunk_index = 0
        self.chunk_questions: Optional[List[Any]] = None
        self.chunk_test_tries = 0

        # Extra API-only helper state. This does not change the learning logic;
        # it only makes the CLI quiz usable from a REST UI.
        self.current_quiz_options: Optional[List[List[str]]] = None
        self.waiting_for_adapt_decision = False
        self.done = False

    def get_current_state(self) -> str:
        return STATES[self.state_index]

    def snapshot(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "current_state": self.get_current_state(),
            "state_index": self.state_index,
            "current_chunk_index": self.current_chunk_index,
            "chunk_test_tries": self.chunk_test_tries,
            "done": self.done,
            "article_title": self.lesson_content["title"] if self.lesson_content else None,
            "chunk_count": len(self.lesson_content["sections"]) if self.lesson_content else 0,
            "current_chunk_title": self._current_chunk_title(),
            "waiting_for_adapt_decision": self.waiting_for_adapt_decision,
        }

    def step(self, input_message: Optional[str] = None, answers: Optional[List[int]] = None) -> Dict[str, Any]:
        current_state = self.get_current_state()

        if current_state == "FETCH":
            return self._fetch(input_message)

        if current_state == "TEACH":
            return self._teach()

        if current_state == "CHECK":
            return self._check(input_message)

        if current_state == "EVAL":
            return self._eval(answers)

        if current_state == "ADAPT":
            return self._adapt(input_message)

        if current_state == "HANDOUT":
            return self._handout()

        raise RuntimeError(f"Unknown state: {current_state}")

    def _base_response(
        self,
        state_before: str,
        message: str,
        requires_input: bool = False,
        input_kind: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "state_before": state_before,
            "state_after": self.get_current_state(),
            "message": message,
            "requires_input": requires_input,
            "input_kind": input_kind,
            "data": data or {},
            "session": self.snapshot(),
        }

    def _fetch(self, input_message: Optional[str]) -> Dict[str, Any]:
        state_before = "FETCH"

        if input_message is None or not input_message.strip():
            return self._base_response(
                state_before=state_before,
                message=(
                    "Welches Thema möchtest du lernen? Bitte gib ein spezifisches Thema an, "
                    "z.B. 'Quantenphysik', 'Photosynthese' oder 'Renaissance Kunst'."
                ),
                requires_input=True,
                input_kind="topic",
            )

        user_input = input_message.strip()
        if user_input.lower() == "exit":
            self.done = True
            return self._base_response(
                state_before=state_before,
                message="Lernassistent wird beendet. Auf Wiedersehen!",
                data={"exit": True},
            )

        # Same topic resolving logic as in your CLI state machine.
        if len(user_input.strip().split(" ")) <= 3:
            resolved_topic = user_input.strip()
        else:
            resolved_topic, _ = ollama_client.llm_chat(
                system_prompt=(
                    "Du bist ein hilfreicher Assistent, der die Benutzereingabe in spezifische Lernthemen auflöst. "
                    "Wenn die Eingabe bereits ein spezifisches Thema ist, gib es unverändert zurück. Selbst wenn die "
                    "Benutzereingabe vage ist, versuche ein spezifisches Thema zu inferieren, das recherchiert und gelernt "
                    "werden kann. Gib nur das aufgelöste Thema ohne zusätzlichen Text zurück. DU DARFST KEINE ERKLÄRUNGEN "
                    "ODER ZUSÄTZLICHEN INFORMATIONEN GEBEN, NUR DAS AUFGELOSTE THEMENTITEL. DU DARFST AUßERDEM DEN "
                    "THEMENTITEL AUCH NICHT IN EIGENEN WORTEN UMFORMULIEREN, WENN DER THEMENTITEL BEREITS SPEZIFISCH GENUG IST. "
                    "WENN DIE BENUTZEREINGABE Z.B. 'QUANTENPHYSIK' IST, GIB 'QUANTENPHYSIK' ZURÜCK, NICHTS ANDERES."
                ),
                message=user_input,
                print_response=False,
            )

        try:
            self.current_chunk_index = 0
            self.lesson_content = wiki_fetcher.get_wikipedia_article(resolved_topic, lang="de")
            self.chunk_questions = None
            self.chunk_test_tries = 0
            self.current_quiz_options = None
            self.waiting_for_adapt_decision = False

            chunk_titles = [section["title"] for section in self.lesson_content["sections"]]
            self.state_index = STATES.index("TEACH")

            return self._base_response(
                state_before=state_before,
                message=(
                    f"Aufgelöstes Thema: {resolved_topic}\n\n"
                    f"Gelesener Wikipedia-Artikel: {self.lesson_content['title']}\n\n"
                    "Der Lernassistent wird nun mit dem ersten Abschnitt beginnen. Viel Erfolg beim Lernen!"
                ),
                data={
                    "resolved_topic": resolved_topic,
                    "article_title": self.lesson_content["title"],
                    "chunk_titles": chunk_titles,
                    "chunk_count": len(chunk_titles),
                },
            )
        except Exception as e:
            return self._base_response(
                state_before=state_before,
                message=(
                    f"Fehler beim Abrufen des Wikipedia-Artikels: {e}\n\n"
                    "Bitte versuche es erneut mit einem anderen Thema oder überprüfe deine Internetverbindung."
                ),
                requires_input=True,
                input_kind="topic",
                data={"error": str(e)},
            )

    def _teach(self) -> Dict[str, Any]:
        state_before = "TEACH"

        if self.lesson_content is None:
            self.state_index = STATES.index("FETCH")
            return self._base_response(
                state_before=state_before,
                message="Es wurde noch kein Artikel geladen. Bitte gib zuerst ein Thema an.",
                requires_input=True,
                input_kind="topic",
            )

        # Same logic as CLI: if no more chunks are available, go to HANDOUT.
        if self.current_chunk_index >= len(self.lesson_content["sections"]):
            self.current_chunk_index = 0
            self.state_index = STATES.index("HANDOUT")
            return self._base_response(
                state_before=state_before,
                message="Alle Abschnitte des Artikels wurden durchgearbeitet.",
            )

        point_of_focus = None
        if self.chunk_questions is not None:
            questions = ", ".join([_get_question_attr(item, "question") for item in self.chunk_questions])
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

        current_section = self.lesson_content["sections"][self.current_chunk_index]
        chunk_summary, _ = ollama_client.llm_chat(
            system_prompt=(
                "Du bist ein hilfreicher Lernassistent, der die folgenden Informationen in einfachen Worten zusammenfasst, "
                "damit ein Schüler sie verstehen kann. Fasse die folgenden Informationen zusammen:\n\n{message}\n\n"
                "Gib nur die Zusammenfassung zurück, ohne zusätzliche Erklärungen oder Informationen. DU DARFST KEINE "
                "ERKLÄRUNGEN ODER ZUSÄTZLICHEN INFORMATIONEN GEBEN, NUR DIE ZUSAMMENFASSUNG DER WICHTIGSTEN PUNKTE "
                "DER INFORMATIONEN, DIE IN EINFACHEN WORTEN FORMULIERT IST, DAMIT EIN SCHÜLER SIE VERSTEHEN KANN. "
                "DIE LÄNGE DER ZUSAMMENFASSUNG SOLL MINIMAL 10 UND MAXIMAL 20 SÄTZE BETRAGEN."
            ),
            message=current_section["content"],
            history=point_of_focus,
            print_response=False,
        )
        current_section["summary"] = chunk_summary

        self.state_index = STATES.index("CHECK")

        return self._base_response(
            state_before=state_before,
            message=chunk_summary,
            data={
                "chunk_index": self.current_chunk_index,
                "chunk_number": self.current_chunk_index + 1,
                "chunk_title": current_section["title"],
                "summary": chunk_summary,
            },
        )

    def _check(self, input_message: Optional[str]) -> Dict[str, Any]:
        state_before = "CHECK"

        if self.lesson_content is None:
            self.state_index = STATES.index("FETCH")
            return self._base_response(
                state_before=state_before,
                message="Es wurde noch kein Artikel geladen. Bitte gib zuerst ein Thema an.",
                requires_input=True,
                input_kind="topic",
            )

        if input_message is None or not input_message.strip():
            return self._base_response(
                state_before=state_before,
                message=f"Möchtest du den Test für den Abschnitt {self.current_chunk_index + 1} starten? (ja/nein)",
                requires_input=True,
                input_kind="start_test_decision",
            )

        user_input = input_message.strip().lower()
        if user_input == "nein":
            self.chunk_test_tries = 0
            self.chunk_questions = None
            self.current_quiz_options = None
            self.current_chunk_index += 1
            self.state_index = STATES.index("TEACH")

            return self._base_response(
                state_before=state_before,
                message="Okay, der Test wird übersprungen.",
                data={"skipped_test": True},
            )

        current_section = self.lesson_content["sections"][self.current_chunk_index]
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
            message=current_section["summary"],
            question_format_on=True,
            print_response=False,
        )

        self.current_quiz_options = []
        public_questions = []
        for index, question in enumerate(self.chunk_questions):
            options = [
                _get_question_attr(question, "true_option"),
                _get_question_attr(question, "distraction_option_1"),
                _get_question_attr(question, "distraction_option_2"),
                _get_question_attr(question, "distraction_option_3"),
            ]
            random.shuffle(options)
            self.current_quiz_options.append(options)
            public_questions.append(
                {
                    "id": index + 1,
                    "question": _get_question_attr(question, "question"),
                    "options": [
                        {"id": option_index + 1, "text": option}
                        for option_index, option in enumerate(options)
                    ],
                }
            )

        self.state_index = STATES.index("EVAL")

        return self._base_response(
            state_before=state_before,
            message="Der Test wurde generiert. Bitte beantworte die Fragen.",
            requires_input=True,
            input_kind="quiz_answers",
            data={
                "chunk_index": self.current_chunk_index,
                "chunk_title": current_section["title"],
                "questions": public_questions,
            },
        )

    def _eval(self, answers: Optional[List[int]]) -> Dict[str, Any]:
        state_before = "EVAL"

        if self.chunk_questions is None or self.current_quiz_options is None:
            self.state_index = STATES.index("CHECK")
            return self._base_response(
                state_before=state_before,
                message="Es wurden noch keine Fragen generiert.",
                requires_input=True,
                input_kind="start_test_decision",
            )

        if answers is None:
            return self._base_response(
                state_before=state_before,
                message="Bitte sende deine Antworten als Liste von Optionsnummern, z.B. [1, 3, 2, 4].",
                requires_input=True,
                input_kind="quiz_answers",
            )

        if len(answers) != len(self.chunk_questions):
            return self._base_response(
                state_before=state_before,
                message=f"Es werden genau {len(self.chunk_questions)} Antworten erwartet.",
                requires_input=True,
                input_kind="quiz_answers",
                data={"expected_answer_count": len(self.chunk_questions), "received_answer_count": len(answers)},
            )

        results = []
        for index, question in enumerate(self.chunk_questions):
            options = self.current_quiz_options[index]
            answer_number = answers[index]

            is_correct = False
            selected_option = None
            try:
                selected_option = options[int(answer_number) - 1]
                is_correct = selected_option == _get_question_attr(question, "true_option")
            except (ValueError, TypeError, IndexError):
                is_correct = False

            _set_answered_correctly(question, is_correct)
            results.append(
                {
                    "id": index + 1,
                    "question": _get_question_attr(question, "question"),
                    "selected_option": selected_option,
                    "correct_option": _get_question_attr(question, "true_option"),
                    "answered_correctly": is_correct,
                }
            )

        self.state_index = STATES.index("ADAPT")

        count_correct = sum(1 for result in results if result["answered_correctly"])
        total = len(results)

        return self._base_response(
            state_before=state_before,
            message=f"Du hast {count_correct} von {total} Fragen richtig beantwortet.",
            data={
                "results": results,
                "count_correct": count_correct,
                "total": total,
                "correct_percentage": count_correct / total if total else 0,
            },
        )

    def _adapt(self, input_message: Optional[str]) -> Dict[str, Any]:
        state_before = "ADAPT"

        if not self.chunk_questions:
            self.state_index = STATES.index("TEACH")
            return self._base_response(
                state_before=state_before,
                message="Keine Testfragen vorhanden. Weiter zum nächsten Schritt.",
            )

        # If the third-failure decision was already requested, process the user's decision here.
        if self.waiting_for_adapt_decision:
            if input_message is None or not input_message.strip():
                return self._base_response(
                    state_before=state_before,
                    message="Möchtest du den Abschnitt nochmals versuchen oder zum nächsten Abschnitt übergehen? (nochmal/skip)",
                    requires_input=True,
                    input_kind="adapt_decision",
                )

            user_input = input_message.strip().lower()
            self.waiting_for_adapt_decision = False

            if user_input == "skip":
                self.chunk_test_tries = 0
                self.chunk_questions = None
                self.current_quiz_options = None
                self.current_chunk_index += 1
                self.state_index = STATES.index("TEACH")

                return self._base_response(
                    state_before=state_before,
                    message="Okay, lass uns zum nächsten Abschnitt übergehen.",
                    data={"decision": "skip"},
                )

            self.state_index = STATES.index("TEACH")
            return self._base_response(
                state_before=state_before,
                message="Okay, lass es uns nochmals durchgehen.",
                data={"decision": "repeat"},
            )

        count_correct = sum(bool(_get_question_attr(q, "answered_correctly")) for q in self.chunk_questions)
        correct_percentage = count_correct / len(self.chunk_questions) if self.chunk_questions else 0
        self.state_index = STATES.index("TEACH")

        if correct_percentage < 0.5:
            self.chunk_test_tries += 1
            self.chunk_questions = [q for q in self.chunk_questions if not bool(_get_question_attr(q, "answered_correctly"))]
            self.current_quiz_options = None

            if self.chunk_test_tries < 3:
                return self._base_response(
                    state_before=state_before,
                    message=(
                        f"Du hast {count_correct} von {len(self.chunk_questions) + count_correct} Fragen richtig beantwortet. "
                        "Es scheint, dass du Schwierigkeiten mit diesem Abschnitt hast. Lass es uns nochmals durchgehen "
                        "und versuchen, die Informationen besser zu verstehen."
                    ),
                    data={
                        "count_correct": count_correct,
                        "correct_percentage": correct_percentage,
                        "next_action": "repeat_chunk",
                    },
                )

            self.waiting_for_adapt_decision = True
            self.state_index = STATES.index("ADAPT")
            return self._base_response(
                state_before=state_before,
                message=(
                    f"Du hast {count_correct} Fragen richtig beantwortet. Es scheint, dass du Schwierigkeiten mit diesem "
                    "Abschnitt hast. Es ist in Ordnung. Möchtest du den Abschnitt nochmals versuchen oder zum nächsten "
                    "Abschnitt übergehen? (nochmal/skip)"
                ),
                requires_input=True,
                input_kind="adapt_decision",
                data={
                    "count_correct": count_correct,
                    "correct_percentage": correct_percentage,
                    "next_action": "ask_repeat_or_skip",
                },
            )

        self.chunk_test_tries = 0
        self.chunk_questions = None
        self.current_quiz_options = None
        self.current_chunk_index += 1

        return self._base_response(
            state_before=state_before,
            message="Gut gemacht! Lass uns zum nächsten Abschnitt übergehen.",
            data={
                "count_correct": count_correct,
                "correct_percentage": correct_percentage,
                "next_action": "next_chunk",
            },
        )

    def _handout(self) -> Dict[str, Any]:
        state_before = "HANDOUT"
        self.done = True
        return self._base_response(
            state_before=state_before,
            message=(
                "HERZLICHEN GLÜCKWUNSCH! DU HAST ALLE ABSCHNITTE DURCHGEARBEITET!\n\n"
                "Handout-State ist noch nicht implementiert."
            ),
            data={"handout": None},
        )

    def _current_chunk_title(self) -> Optional[str]:
        if self.lesson_content is None:
            return None
        if self.current_chunk_index >= len(self.lesson_content["sections"]):
            return None
        return self.lesson_content["sections"][self.current_chunk_index]["title"]


class SessionStore:
    """Simple in-memory session store for the MVP REST API."""

    def __init__(self):
        self._sessions: Dict[str, LearningSession] = {}

    def create(self) -> LearningSession:
        session = LearningSession()
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> LearningSession:
        if session_id not in self._sessions:
            raise KeyError(session_id)
        return self._sessions[session_id]

    def delete(self, session_id: str) -> None:
        if session_id in self._sessions:
            del self._sessions[session_id]

    def list(self) -> List[Dict[str, Any]]:
        return [session.snapshot() for session in self._sessions.values()]
