from aiogram.fsm.state import State, StatesGroup

class Profile(StatesGroup):
    name = State()
    age = State()
    gender = State()
    city = State()
    goal = State()
    target_gender = State()
    username = State()
    photo = State()
    confirm = State()
    edit_field = State()

class PsychologicalTest(StatesGroup):
    welcome = State()          
    in_progress = State()    
    paused = State()           
    results = State()          
    confirm_retake = State()