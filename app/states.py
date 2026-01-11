from aiogram.fsm.state import State, StatesGroup

class RegistrationState(StatesGroup):
    WAITING_FOR_PHONE = State()
    WAITING_FOR_NAME = State() # Optional, if we want to ask name manually if not in contact

class RideOfferState(StatesGroup):
    START_LOC = State()
    END_LOC = State()
    DATE = State()
    TIME = State()
    SEATS = State()
    CAR_MODEL = State()
    PHOTO = State()

class RideRequestState(StatesGroup):
    START_LOC = State()
    END_LOC = State()
    DATE = State()
    TIME = State()
    SEATS = State()
