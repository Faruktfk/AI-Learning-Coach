
from core import state_machine


while True:

   state, user_input = state_machine.run_state_machine()
   
   if user_input is not None and user_input.lower() == 'exit':
        break
    
    

