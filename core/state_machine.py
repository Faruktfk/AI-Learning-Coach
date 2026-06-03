from tools import ollama_client, wiki_fetcher


STATES = ["FETCH", "TEACH", "CHECK", "EVAL", "ADAPT", "HANDOUT"]

STATE_INDEX = 0

LESSON_CONTENT = None

CURRENT_CHUNK_INDEX = 0

def get_current_state():
    return STATES[STATE_INDEX]

def run_state_machine(input_message=None):
    global STATE_INDEX
    
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
        resolved_topic, _= ollama_client.llm_chat(
            system_prompt="Du bist ein hilfreicher Assistent, der die Benutzereingabe in spezifische Lernthemen auflöst. Wenn die Eingabe bereits ein spezifisches Thema ist, gib es unverändert zurück. Selbst wenn die Benutzereingabe vage ist, versuche ein spezifisches Thema zu inferieren, das recherchiert und gelernt werden kann. Gib nur das aufgelöste Thema ohne zusätzlichen Text zurück. DU DARFST KEINE ERKLÄRUNGEN ODER ZUSÄTZLICHEN INFORMATIONEN GEBEN, NUR DAS AUFGELOSTE THEMENTITEL. DU DARFST AUßERDEM DEN THEMENTITEL AUCH NICHT IN EIGENEN WORTEN UMFORMULIEREN, WENN DER THEMENTITEL BEREITS SPEZIFISCH GENUG IST. WENN DIE BENUTZEREINGABE Z.B. 'QUANTENPHYSIK' IST, GIB 'QUANTENPHYSIK' ZURÜCK, NICHTS ANDERES.",
            message=user_input
        )

        print(f"\n\nAufgelöstes Thema: {resolved_topic}\n\n")

        # Fetch relevant wiki article
        # Split article in chunks
        try:
            chunk_titles = ""
            LESSON_CONTENT = wiki_fetcher.get_wikipedia_article(resolved_topic, lang="de")
            print(f"\n\nGelesener Wikipedia-Artikel: {LESSON_CONTENT['title']}\n\n")
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
        # Summarize a chunk
        chunk_summary, _= ollama_client.llm_chat(
            system_prompt="Du bist ein hilfreicher Lernassistent, der die folgenden Informationen in einfachen Worten zusammenfasst, damit ein Schüler sie verstehen kann. Fasse die folgenden Informationen zusammen:\n\n{message}\n\nGib nur die Zusammenfassung zurück, ohne zusätzliche Erklärungen oder Informationen. DU DARFST KEINE ERKLÄRUNGEN ODER ZUSÄTZLICHEN INFORMATIONEN GEBEN, NUR DIE ZUSAMMENFASSUNG DER WICHTIGSTEN PUNKTE DER INFORMATIONEN, DIE IN EINFACHEN WORTEN FORMULIERT IST, DAMIT EIN SCHÜLER SIE VERSTEHEN KANN.",
            message=LESSON_CONTENT["sections"][CURRENT_CHUNK_INDEX]['content']
        )

        # Focus on failed questions

        # USER OUTPUT -> Lesson

        # Change to CHECK state
        STATE_INDEX += 1
    
    elif current_state == "CHECK":
        # Generate 5 questions from the chunk summary and ask the user

        # USER OUTPUT -> Questions

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
        
        a = "a"

    print(f"Current state: {current_state}, User input: {user_input}")
    return current_state, user_input