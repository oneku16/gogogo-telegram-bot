from aiogram.fsm.state import State, StatesGroup

class RegistrationState(StatesGroup):
    WAITING_FOR_LANGUAGE = State()
    WAITING_FOR_PHONE = State()
    WAITING_FOR_ROLE = State()
    WAITING_FOR_NAME = State() # Optional, if we want to ask name manually if not in contact

class RideOfferState(StatesGroup):
    START_LOC = State()
    END_LOC = State()
    DATE = State()
    TIME = State()
    SEATS = State()
    CAR_MODEL = State()
    PRICE = State()
    CONFIRMATION = State()

class RideRequestState(StatesGroup):
    START_LOC = State()
    END_LOC = State()
    DATE = State()
    TIME = State()
    SEATS = State()
    CONFIRMATION = State()

class EditPostState(StatesGroup):
    CONFIRM_REFILE = State()
    TARGET_ID = State() # Store ID to delete
    TARGET_TYPE = State() # 'offer' or 'request'
