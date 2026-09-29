from aiogram.fsm.state import State, StatesGroup

class AddQuestionFSM(StatesGroup):
    category = State()
    difficulty = State()
    question = State()
    options = State()
    correct = State()
    explanation = State()

class BroadcastFSM(StatesGroup):
    message = State()