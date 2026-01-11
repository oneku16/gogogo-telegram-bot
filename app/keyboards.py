from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_phone_request_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Share Phone Number", request_contact=True)]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def get_main_menu_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="I am a Driver 🚗")],
        [KeyboardButton(text="I am a Passenger 🧍")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_cancel_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="Cancel ❌")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
