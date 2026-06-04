import random

from tools import ollama_client, wiki_fetcher


STATES = ["FETCH", "TEACH", "CHECK", "EVAL", "ADAPT", "HANDOUT"]

STATE_INDEX = 0

LESSON_CONTENT = None

CURRENT_CHUNK_INDEX = 0

CHUNK_QUESTIONS = None

CHUNK_TEST_TRIES = 0

def get_current_state():
    return STATES[STATE_INDEX]

def run_state_machine(input_message=None):
    global STATE_INDEX, LESSON_CONTENT, CURRENT_CHUNK_INDEX, CHUNK_QUESTIONS, CHUNK_TEST_TRIES
    
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
        print(f"\n\nAufgelöstes Thema:\n")
        if len(user_input.strip().split(" ")) <= 3:
            resolved_topic = user_input.strip()
            print(f"{resolved_topic}")
        else:
            resolved_topic, _= ollama_client.llm_chat(
                system_prompt="Du bist ein hilfreicher Assistent, der die Benutzereingabe in spezifische Lernthemen auflöst. Wenn die Eingabe bereits ein spezifisches Thema ist, gib es unverändert zurück. Selbst wenn die Benutzereingabe vage ist, versuche ein spezifisches Thema zu inferieren, das recherchiert und gelernt werden kann. Gib nur das aufgelöste Thema ohne zusätzlichen Text zurück. DU DARFST KEINE ERKLÄRUNGEN ODER ZUSÄTZLICHEN INFORMATIONEN GEBEN, NUR DAS AUFGELOSTE THEMENTITEL. DU DARFST AUßERDEM DEN THEMENTITEL AUCH NICHT IN EIGENEN WORTEN UMFORMULIEREN, WENN DER THEMENTITEL BEREITS SPEZIFISCH GENUG IST. WENN DIE BENUTZEREINGABE Z.B. 'QUANTENPHYSIK' IST, GIB 'QUANTENPHYSIK' ZURÜCK, NICHTS ANDERES.",
                message=user_input
            )

        
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
        # Go to HANDOUT state if no more chunks are available
        if CURRENT_CHUNK_INDEX >= len(LESSON_CONTENT["sections"]):
            print(f"\n\nAlle Abschnitte des Artikels wurden durchgearbeitet. \n\n")
            CURRENT_CHUNK_INDEX = 0
            STATE_INDEX = 5

        else:
            # Focus on failed questions
            point_of_focus = None
            if CHUNK_QUESTIONS is not None:
                questions = ', '.join([item['question'] for item in CHUNK_QUESTIONS])
                point_of_focus = [{"role": "user", "content": f"In der nächsten Zusammenfassung sollst du dich auf die folgenden Fragen konzentrieren: [{questions}]. Wenn du die folgenden Informationen zusammenfasst, versuche besonders die Informationen hervorzuheben, die für die Beantwortung dieser Fragen relevant sind."}]


            # USER OUTPUT -> Lesson
            print("\n\n\n", "="*10, f" {CURRENT_CHUNK_INDEX + 1}. {LESSON_CONTENT['sections'][CURRENT_CHUNK_INDEX]['title'].upper()} ", "="*10, "\n")
            # Summarize a chunk
            chunk_summary, _= ollama_client.llm_chat(
                system_prompt="Du bist ein hilfreicher Lernassistent, der die folgenden Informationen in einfachen Worten zusammenfasst, damit ein Schüler sie verstehen kann. Fasse die folgenden Informationen zusammen:\n\n{message}\n\nGib nur die Zusammenfassung zurück, ohne zusätzliche Erklärungen oder Informationen. DU DARFST KEINE ERKLÄRUNGEN ODER ZUSÄTZLICHEN INFORMATIONEN GEBEN, NUR DIE ZUSAMMENFASSUNG DER WICHTIGSTEN PUNKTE DER INFORMATIONEN, DIE IN EINFACHEN WORTEN FORMULIERT IST, DAMIT EIN SCHÜLER SIE VERSTEHEN KANN. DIE LÄNGE DER ZUSAMMENFASSUNG SOLL MINIMAL 10 UND MAXIMAL 20 SÄTZE BETRAGEN.",
                message=LESSON_CONTENT["sections"][CURRENT_CHUNK_INDEX]['content'],
                history=point_of_focus
            )
            LESSON_CONTENT["sections"][CURRENT_CHUNK_INDEX]['summary'] = chunk_summary

            
            # Change to CHECK state
            STATE_INDEX += 1



    
    
    elif current_state == "CHECK":
        user_input = input(f"\n\n Assistent: Möchtest du den Test für den Abschnitt {CURRENT_CHUNK_INDEX + 1} starten? (ja/nein) \n\n > ")
        if user_input.lower() == 'nein':
            print(f"\n\nOkay, der Test wird übersprungen. \n\n")
            CHUNK_TEST_TRIES = 0
            CHUNK_QUESTIONS = None
            CURRENT_CHUNK_INDEX += 1
            STATE_INDEX = 1
        else:
            print("\n\nGeneriere Fragen...\n\n")
            
            # Generate 3-8 multiple-choice questions from the chunk summary and ask the user
            CHUNK_QUESTIONS, _= ollama_client.llm_chat(
                system_prompt="Du bist ein hilfreicher Lernassistent, der basierend auf den folgenden Informationen 3 bis 8 Multiple-Choice-Fragen generiert, um das Verständnis eines Schülers zu überprüfen. Generiere Fragen, die sich auf die wichtigsten Punkte der Informationen konzentrieren und das Verständnis des Schülers testen. DU DARFST KEINE ERKLÄRUNGEN ODER ZUSÄTZLICHEN INFORMATIONEN GEBEN. DU SOLLST DIE FRAGEN IN FOLGENDEN FORMAT GENERIEREN: JEDES FRAGE-ANTWORT-SET SOLL EIN DICT SEIN, DAS DIE FOLGENDEN FELDER ENTHÄLT: 'question' (die Frage), 'true_option' (die richtige Antwortoption), 'distraction_option_1' (eine falsche Antwortoption), 'distraction_option_2' (eine falsche Antwortoption) und 'distraction_option_3' (eine falsche Antwortoption). GIB NUR DIE FRAGEN IM ANGEGEBENEN JSON-FORMAT ZURÜCK, OHNE ZUSÄTZLICHE ERKLÄRUNGEN ODER INFORMATIONEN.",
                message=LESSON_CONTENT['sections'][CURRENT_CHUNK_INDEX]['summary'],
                question_format_on=True,
                print_response=False
            )

            # Change to EVALUATE state
            STATE_INDEX += 1
    
    
    
    
    
    
    elif current_state == "EVAL":
        # USER INPUT/OUTPUT -> Answers and Questions
        print("\n\n\n", "="*10, f" TEST: {CURRENT_CHUNK_INDEX + 1}. {LESSON_CONTENT['sections'][CURRENT_CHUNK_INDEX]['title'].upper()} -- {len(CHUNK_QUESTIONS)} Fragen -- {CHUNK_QUESTIONS}. Try ", "="*10, "\n")
        for i, q in enumerate(CHUNK_QUESTIONS):
            print(f"\nFrage {i+1}: {q.question}\n")
            options = [q.true_option, q.distraction_option_1, q.distraction_option_2, q.distraction_option_3]
            random.shuffle(options)
            for j, option in enumerate(options):
                print(f"{j+1}. {option}")
            user_answer = input("\nDeine Antwort (bitte die Nummer der gewählten Option eingeben): ")
            try:
                user_answer_index = int(user_answer) - 1
                if options[user_answer_index] == q.true_option:
                    print("Richtig!")
                    q.answered_correctly = True
                else:
                    print(f"Falsch! Die richtige Antwort wäre: {q.true_option}")
                    q.answered_correctly = False
            except (ValueError, IndexError):
                print(f"Ungültige Eingabe! Die richtige Antwort wäre: {q.true_option}")
                q.answered_correctly = False
        
        # Change to ADAPT state
        STATE_INDEX += 1
    
    
    
    
    
    elif current_state == "ADAPT":
        count_correct = sum(q.answered_correctly for q in CHUNK_QUESTIONS)
        correct_percentage = count_correct / len(CHUNK_QUESTIONS) if CHUNK_QUESTIONS else 0
        STATE_INDEX = 1

        print(f"\n\nDu hast {count_correct} von {len(CHUNK_QUESTIONS)} Fragen richtig beantwortet. ({correct_percentage:.2%})\n\n")

        if(correct_percentage < 0.5):
            CHUNK_TEST_TRIES += 1
            CHUNK_QUESTIONS = filter(lambda q: not q.answered_correctly, CHUNK_QUESTIONS)
            
            if(CHUNK_TEST_TRIES < 3):    
                print(f"\n\nEs scheint, dass du Schwierigkeiten mit diesem Abschnitt hast. Lass es uns nochmals durchgehen und versuchen, die Informationen besser zu verstehen. \n\n")
            
            else:    
                print("Es scheint, dass du Schwierigkeiten mit diesem Abschnitt hast. Es ist in Ordnung.")
                user_input = input("Möchtest du den Abschnitt nochmals versuchen oder zum nächsten Abschnitt übergehen? (nochmal/skip) \n\n > ")
                if user_input.lower() == 'nochmals':
                    print(f"\n\nOkay, lass es uns nochmals durchgehen. \n\n")
                else:
                    print(f"\n\nOkay, lass uns zum nächsten Abschnitt übergehen. \n\n")
                    CHUNK_TEST_TRIES = 0
                    CHUNK_QUESTIONS = None
                    CURRENT_CHUNK_INDEX += 1

        else:
            print(f"\n\nGut gemacht! Lass uns zum nächsten Abschnitt übergehen. \n\n")
            CHUNK_TEST_TRIES = 0
            CHUNK_QUESTIONS = None
            CURRENT_CHUNK_INDEX += 1

    
    
    
    
    
    elif current_state == "HANDOUT":
        # USER OUTPUT -> Handout
        print("\n\n\n", "="*20, "\n")
        print("HERZLICHEN GLÜCKWUNSCH! DU HAST ALLE ABSCHNITTE DURCHGEARBEITET!\n")
        print("Handout wird generiert...")

        # Generate handout with all summaries

        # End of the loop
        
        user_input = "exit"

    print(f"Current state: {current_state}, User input: {user_input}")
    return current_state, user_input