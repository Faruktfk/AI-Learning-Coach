
STATES = ["FETCH", "TEACH", "CHECK", "EVAL", "ADAPT", "HANDOUT"]

STATE_INDEX = 0

def get_current_state():
    return STATES[STATE_INDEX]

def run_state_machine(input_message=None):
    global STATE_INDEX
    
    user_input = input_message

    current_state = get_current_state()
    
    if current_state == "FETCH":
        # USER INPUT -> Topic
        user_input = input('\n > ')

        # Resolve topic

        # Fetch relevant wiki article

        # Split article in chunks

        # Change to TEACH state
        STATE_INDEX += 0
    
    elif current_state == "TEACH":
        # Summarize a chunk

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