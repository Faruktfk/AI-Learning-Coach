from tools import ollama_client, wiki_fetcher


STATES = ["FETCH", "TEACH", "CHECK", "EVAL", "ADAPT", "HANDOUT"]

STATE_INDEX = 0

LESSON_CONTENT = None

CURRENT_CHUNK_INDEX = 0

CHUNK_QUESTIONS = None

def get_current_state():
    return STATES[STATE_INDEX]

def run_state_machine(input_message=None):
    global STATE_INDEX, LESSON_CONTENT, CURRENT_CHUNK_INDEX, CHUNK_QUESTIONS
    
    user_input = input_message

    current_state = get_current_state()
    
    if current_state == "FETCH":
        # USER INPUT -> Topic
        message = "Welches Thema möchtest du lernen? Bitte gib ein spezifisches Thema an, z.B. 'Quantenphysik', 'Photosynthese' oder 'Renaissance Kunst'. \n('exit' um zu beenden)"
        user_input = input(f"\n\n Assistent: {message} \n\n > ")

        if user_input.lower() == 'exit':
            print("\n\nLernassistent wird beendet. Auf Wiedersehen!\n\n")
            return current_state, user_input

        # Resolve topic
        if len(user_input.strip().split(" ")) <= 3:
            resolved_topic = user_input.strip()
        else:
            resolved_topic, _= ollama_client.llm_chat(
                system_prompt="Du bist ein hilfreicher Assistent, der die Benutzereingabe in spezifische Lernthemen auflöst. Wenn die Eingabe bereits ein spezifisches Thema ist, gib es unverändert zurück. Selbst wenn die Benutzereingabe vage ist, versuche ein spezifisches Thema zu inferieren, das recherchiert und gelernt werden kann. Gib nur das aufgelöste Thema ohne zusätzlichen Text zurück. DU DARFST KEINE ERKLÄRUNGEN ODER ZUSÄTZLICHEN INFORMATIONEN GEBEN, NUR DAS AUFGELOSTE THEMENTITEL. DU DARFST AUßERDEM DEN THEMENTITEL AUCH NICHT IN EIGENEN WORTEN UMFORMULIEREN, WENN DER THEMENTITEL BEREITS SPEZIFISCH GENUG IST. WENN DIE BENUTZEREINGABE Z.B. 'QUANTENPHYSIK' IST, GIB 'QUANTENPHYSIK' ZURÜCK, NICHTS ANDERES.",
                message=user_input
            )

        print(f"\n\nAufgelöstes Thema: {resolved_topic}\n\n")

        # Fetch relevant wiki article
        # Split article in chunks
        try:
            CURRENT_CHUNK_INDEX = 0
            LESSON_CONTENT = wiki_fetcher.get_wikipedia_article(resolved_topic, lang="de")
            print(f"\n\nGelesener Wikipedia-Artikel: {LESSON_CONTENT['title']}\n\n")
            chunk_titles = ""
            for t in LESSON_CONTENT["sections"]:
                chunk_titles += t['title'] + " | "

            print(f"\n\nArtikel in folgende Abschnitte unterteilt:\n{chunk_titles}\n\n")
            print(f"\n\nDer Lernassistent wird nun mit dem ersten Abschnitt beginnen. Viel Erfolg beim Lernen!\n\n")
            
            # Change to TEACH state
            STATE_INDEX += 1
        except Exception as e:
            print(f"\n\nFehler beim Abrufen des Wikipedia-Artikels: {e}\n\n")
            print(f"\n\nBitte versuche es erneut mit einem anderen Thema oder überprüfe deine Internetverbindung.\n\n")
            # Stay in FETCH state and ask again
            STATE_INDEX += 0

    elif current_state == "TEACH":

        # Focus on failed questions
        point_of_focus = None
        if CHUNK_QUESTIONS is not None:
            questions = ', '.join([item['question'] for item in CHUNK_QUESTIONS])
            point_of_focus = [{"role": "user", "content": f"In der nächsten Zusammenfassung sollst du dich auf die folgenden Fragen konzentrieren: [{questions}]. Wenn du die folgenden Informationen zusammenfasst, versuche besonders die Informationen hervorzuheben, die für die Beantwortung dieser Fragen relevant sind."}]
        
        # Summarize a chunk
        chunk_summary, _= ollama_client.llm_chat(
            system_prompt="Du bist ein hilfreicher Lernassistent, der die folgenden Informationen in einfachen Worten zusammenfasst, damit ein Schüler sie verstehen kann. Fasse die folgenden Informationen zusammen:\n\n{message}\n\nGib nur die Zusammenfassung zurück, ohne zusätzliche Erklärungen oder Informationen. DU DARFST KEINE ERKLÄRUNGEN ODER ZUSÄTZLICHEN INFORMATIONEN GEBEN, NUR DIE ZUSAMMENFASSUNG DER WICHTIGSTEN PUNKTE DER INFORMATIONEN, DIE IN EINFACHEN WORTEN FORMULIERT IST, DAMIT EIN SCHÜLER SIE VERSTEHEN KANN. DIE LÄNGE DER ZUSAMMENFASSUNG SOLL MINIMAL 10 UND MAXIMAL 20 SÄTZE BETRAGEN.",
            message=LESSON_CONTENT["sections"][CURRENT_CHUNK_INDEX]['content'],
            history=point_of_focus
        )
        LESSON_CONTENT["sections"][CURRENT_CHUNK_INDEX]['summary'] = chunk_summary

        # USER OUTPUT -> Lesson
        print("\n\n\n", "="*10, f" {CURRENT_CHUNK_INDEX + 1}. {LESSON_CONTENT['sections'][CURRENT_CHUNK_INDEX]['title'].upper()} ", "="*10)
        print(f"\n\n{chunk_summary}\n\n")

        # Change to CHECK state
        STATE_INDEX += 1
    
    elif current_state == "CHECK":
        print("\n\nGeneriere Fragen...\n\n")

        # Generate 5 questions from the chunk summary and ask the user
        raw_chunk_questions, _= ollama_client.llm_chat(
            system_prompt="Du bist ein hilfreicher Lernassistent, der basierend auf den folgenden Informationen 3 bis 8 Fragen generiert, um das Verständnis eines Schülers zu überprüfen. Generiere 5 Fragen, die sich auf die wichtigsten Punkte der Informationen konzentrieren und das Verständnis des Schülers testen. Gib die Fragen in der folgenden JSON-Format zurück: [{\"question\": \"Frage 1\", \"answer\": \"Die richtige Antwort auf Frage 1\"}, {\"question\": \"Frage 2\", \"answer\": \"Die richtige Antwort auf Frage 2\"}, ...]. DU DARFST KEINE ERKLÄRUNGEN ODER ZUSÄTZLICHEN INFORMATIONEN GEBEN, NUR DIE FRAGEN UND RICHTIGEN ANTWORTEN IM ANGEGEBENEN JSON-FORMAT. WICHTIG: DIE RICHTIGEN ANTWORTEN SOLLEN IN EINFACHEN WORTEN FORMULIERT SEIN, DAMIT EIN SCHÜLER SIE VERSTEHEN KANN.",
            message=LESSON_CONTENT['sections'][CURRENT_CHUNK_INDEX]['summary']
        )
        # USER OUTPUT -> Questions
        print("\n\n\n", "="*10, f" TEST: {CURRENT_CHUNK_INDEX + 1}. {LESSON_CONTENT['sections'][CURRENT_CHUNK_INDEX]['title'].upper()} ", "="*10)
        print(f"\n\n{raw_chunk_questions}\n\n")

        # Change to EVALUATE state
        STATE_INDEX += 1
    
    elif current_state == "EVAL":
        # USER INPUT -> Answers

        # Evaluate user's answers by semantic similarity

        # Change to ADAPT state
        STATE_INDEX += 1
    
    elif current_state == "ADAPT":
        # USER OUTPUT -> Test Results

        # Result Logic
        
        # TODO: Logic...
        
        STATE_INDEX += 1
    
    elif current_state == "HANDOUT":
        # USER OUTPUT -> Handout
        
        # End of the loop
        
        user_input = "exit"

    print(f"Current state: {current_state}, User input: {user_input}")
    return current_state, user_input